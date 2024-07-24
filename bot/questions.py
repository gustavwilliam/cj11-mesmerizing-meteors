import asyncio
import re
from abc import abstractmethod
from typing import Protocol

from utils.eval import eval_python

check_test = re.compile(r"Ran 1 test in \S+s\n\nOK\n$")  # Successful unit tests output should end with this


class Question(Protocol):
    """Protocol that all questions must implement.

    Different question types can be created by subclassing this protocol.
    """

    question: str
    hints: list[str]

    def __str__(self) -> str:
        """Return the question text."""
        return self.question

    @abstractmethod
    def check_response(self, response: str) -> bool:
        """Check if the answer is correct."""
        raise NotImplementedError


class MultipleChoiceQuestion(Question):
    """A type of Level where the user selects the correct answer from multiple choices."""

    def __init__(self, question: str, hints: list[str], options: list[str], answer: str) -> None:
        self.question = question
        self.hints = hints
        self.options = options
        self.answer = answer

    def check_response(self, response: str) -> bool:  # noqa: D102
        return response == self.answer


class WriteCodeQuestion(Question):
    """A type of Level where the user writes code to solve a problem."""

    def __init__(self, question: str, hints: list[str], test_cases: list[tuple[str, str]]) -> None:
        self.question = question
        self.hints = hints
        self.test_cases = test_cases

    async def check_response(self, code: str) -> bool:
        """Check if the code answer is correct.

        Runs a suite of unit tests on the code. If they all pass, the code is deemed correct.

        Raises an error if a connection to the code evaluation service fails.
        """
        test_string = self._get_test_string(code)
        output = await eval_python(test_string)
        return bool(check_test.search(output))  # If unit tests pass, the code is correct

    @staticmethod
    def _get_assert_equal_string(input: str, output: str) -> str:
        """Return a code string that asserts if the input and output are equal.

        Input and output strings will be parsed and interpreted as raw Python code.
        For example, if a value is supposed to be a string, it should be enclosed in quotes.

        Example:
        -------
        >>> get_assert_equal_string("uwuify('hello')", "'hewwo'")  # Include quotes around "hewwo"
        "self.assetEqual(uwuify('hello'), 'hewwo')"

        """
        return f"self.assertEqual({input},{output})"

    def _get_test_string(self, user_code: str) -> str:
        """Return the test string to be used in the code evaluation service.

        This is not an optimal way of testing code, but it is fairly straightforward and easy to implement for now.
        It can cause bugs if the input and output strings are not formatted correctly, which might not be trivial
        to debug. However, since the code is running in a sandboxed environment, this method of generating tests
        poses no security risk.
        """
        test_strings = [self._get_assert_equal_string(*test_case) for test_case in self.test_cases]
        return (
            "import unittest\n"  # Import unittest module
            + user_code.expandtabs(2)  # Insert user code. Tabs -> spaces for consistency with test code
            + "\nclass Test(unittest.TestCase):\n"  # Setup test class
            + " def test_cases(self):"  # Setup test method
            + "\n  "  # Indentation for first test case
            + "\n  ".join(test_strings)  # Add assertions for test cases
            + "\nunittest.main()"  # Run unit tests
        )


def question_factory(**question_data) -> Question:  # noqa: ANN003
    """Create Question instance using the correct Question subclass."""
    match question_data.get("type"):
        case "multiple_choice":
            return MultipleChoiceQuestion(**question_data)
        case "write_code":
            return WriteCodeQuestion(**question_data)
        case _:
            raise ValueError


if __name__ == "__main__":
    # Example code for testing purposes. Will be removed in later nevels of the
    write_code_question = WriteCodeQuestion(
        question="Write an `add` function that adds two numbers.",
        hints=["Is your function named exactly `add`?", "Remember to use the `return` keyword."],
        test_cases=[("add(1, 2)", "3"), ("add(-1,3)", "2")],
    )
    code = """def add(a, b):
    return a + b"""
    output = asyncio.run(write_code_question.check_response(code))
    print(f"\n{output}")
