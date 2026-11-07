from loom.agent import Agent
from loom.index import Vectorize

from .parser import parse_questions
from .report import write_baseline, write_report


class Evaluator:
    def __init__(self):
        self.vectorizer = Vectorize()
        self.agent = Agent()
        self.questions = None

    def __load_questions(self):
        try:
            questions = parse_questions()
            self.questions = questions
            return questions
        except (FileNotFoundError, OSError, TimeoutError, ConnectionError) as e:
            print(f"Loading Questions Failed: {e}")

    def evaluate_questions(self):
        try:
            if self.questions is None:
                self.__load_questions()

            questions_results = [({"result": self.vectorizer.search_vector(question_dict["question"]), "question": question_dict}) for question_dict in self.questions]
            write_report(questions_results)

        except (FileNotFoundError, OSError, TimeoutError, ConnectionError) as e:
            print(f"Evaluation Failed: {e}")


    def evaluate_questions_llm(self):
        try:
            if self.questions is None:
                self.__load_questions()

            questions_results = [
                {"result": self.agent.answer(question_dict["question"]), "question": question_dict}
                for question_dict in self.questions
            ]
            write_baseline(questions_results)

        except (FileNotFoundError, OSError, TimeoutError, ConnectionError) as e:
            print(f"Evaluation Failed: {e}")


if __name__=="__main__":
    evaluator = Evaluator()
    evaluator.evaluate_questions()