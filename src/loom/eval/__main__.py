from loom.agent import Agent
from loom.index import Vectorize

from .parser import parse_questions
from .report import succeeded_question_ids, write_baseline, write_report


class Evaluator:
    def __init__(self):
        self.vectorizer = Vectorize()
        self.agent = None
        self.questions = None

    def __get_agent(self):
        if self.agent is None:
            self.agent = Agent(vectorizer=self.vectorizer)
        return self.agent

    def __load_questions(self):
        try:
            questions = parse_questions()
            if not questions:
                raise ValueError("No questions found")
            self.questions = questions
            print(f"{len(questions)} Questions Loaded.")
            return questions
        except (FileNotFoundError, OSError, TimeoutError, ConnectionError) as e:
            print(f"Loading Questions Failed: {e}")

    def evaluate_questions(self):
        try:
            if self.questions is None:
                self.__load_questions()

            questions_results = [
                (
                    {
                        "result": self.vectorizer.search_vector(
                            question_dict["question"]
                        ),
                        "question": question_dict,
                    }
                )
                for question_dict in self.questions
            ]
            print("Writing Reports.")
            write_report(questions_results)
            print("Done Writing Reports.")

        except (FileNotFoundError, OSError, TimeoutError, ConnectionError) as e:
            print(f"Evaluation Failed: {e}")

    def evaluate_questions_llm(self):
        try:
            if self.questions is None:
                self.__load_questions()

            done = succeeded_question_ids()
            pending = [q for q in self.questions if q["id"] not in done]
            if not pending:
                print("All questions already have a recorded result in baseline.md.")
                return

            print(f"Re-running {len(pending)}/{len(self.questions)} pending question(s).")
            agent = self.__get_agent()
            questions_results = [
                {
                    "result": agent.answer(question_dict["question"]),
                    "question": question_dict,
                }
                for question_dict in pending
            ]
            write_baseline(questions_results)

        except (FileNotFoundError, OSError, TimeoutError, ConnectionError) as e:
            print(f"Evaluation Failed: {e}")


if __name__ == "__main__":
    evaluator = Evaluator()
    evaluator.evaluate_questions()
