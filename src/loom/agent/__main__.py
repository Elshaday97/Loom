import os
import time
from http import HTTPStatus

from google import genai
from google.genai import errors, types

from loom.index import Vectorize

SYSTEM_INSTRUCTION = (
    "Answer using only the code context provided below. Cite the specific "
    "file and line range you drew from. If the context doesn't contain "
    "enough information to answer, say so rather than guessing."
)


class Agent:
    def __init__(self, vectorizer: Vectorize = None):
        self.vectorizer = vectorizer or Vectorize()
        self.client = genai.Client(
            api_key=os.environ["FRONTIER_API_KEY"],
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    initial_delay=1.0,
                    attempts=5,
                    http_status_codes=[
                        HTTPStatus.REQUEST_TIMEOUT,
                        HTTPStatus.TOO_MANY_REQUESTS,
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        HTTPStatus.BAD_GATEWAY,
                        HTTPStatus.SERVICE_UNAVAILABLE,
                        HTTPStatus.GATEWAY_TIMEOUT,
                    ],
                ),
                timeout=120 * 1000,
            ),
        )

    def __build_context(self, results: list[dict]) -> str:
        blocks = []
        for i, r in enumerate(results, start=1):
            chunk = r["result"]
            blocks.append(
                f"[Source {i}: {chunk['path']}:{chunk['start_line']}-{chunk['end_line']}]\n"
                f"{chunk['text']}"
            )
        return "\n\n".join(blocks)

    def answer(self, question: str, k: int = 5):
        results = self.vectorizer.search_vector(question, k)
        if not results:
            return {
                "answer": None,
                "error": "No relevant context found",
                "sources": [],
                "latency_s": 0.0,
                "input_tokens": None,
                "output_tokens": None,
            }

        context = self.__build_context(results)
        contents = f"Context:\n{context}\n\nQuestion: {question}"

        start = time.monotonic()
        try:
            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION
                ),
            )
        except errors.ServerError as e:
            return self.__error_result(
                f"Gemini server error: {e.message}", results, start
            )
        except errors.ClientError as e:
            if e.code == 429:
                return self.__error_result("Rate limited", results, start)
            if e.code in (401, 403):
                return self.__error_result(
                    "Auth failed — check API key", results, start
                )
            return self.__error_result(f"Client error: {e.message}", results, start)
        except errors.APIError as e:
            return self.__error_result(f"API error: {e.message}", results, start)

        latency = time.monotonic() - start
        usage = response.usage_metadata
        return {
            "answer": response.text,
            "error": None,
            "sources": results,
            "latency_s": latency,
            "input_tokens": usage.prompt_token_count,
            "output_tokens": usage.candidates_token_count,
        }

    def __error_result(self, message: str, results: list[dict], start: float) -> dict:
        return {
            "answer": None,
            "error": message,
            "sources": results,
            "latency_s": time.monotonic() - start,
            "input_tokens": None,
            "output_tokens": None,
        }
