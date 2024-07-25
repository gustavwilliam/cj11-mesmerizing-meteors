import re
import typing
from abc import abstractmethod
from enum import Enum, auto
from typing import Protocol

import discord
from discord import Embed, Interaction
from discord.ui.view import View
from utils.eval import eval_python

if typing.TYPE_CHECKING:
    from levels import Level

check_test = re.compile(r"Ran 1 test in \S+s\n\nOK\n$")  # Successful unit tests output should end with this


class Question(Protocol):
    """Protocol that all questions must implement.

    Different question types can be created by subclassing this protocol.

    The general structure of a question's JSON data is as follows:
    {
        "question": "What is 2 + 2?",
        "hints": [
            "Remember the order of operations."
            ...
        ],
        "type": "multiple_choice",
    }

    The `hints` field is a list of strings that provide hints to the user. If the hints are requested
    by the user, they will be shown in the order that they are listed in the JSON data.

    The `question` field is a string that contains the question text.

    The `type` field determines the type of question. The following types are currently supported:
    - "multiple_choice": The user selects the correct answer from multiple choices
    - "write_code": The user writes Python code to solve a problem

    Depending on what the `type` field is set to, there are additional fields that must be included in the JSON data.
    The additional fields can be found in the docstrings of the specific Question subclasses.
    """

    type: str
    question: str
    hints: list[str]

    def __str__(self) -> str:
        """Return the question text."""
        return self.question

    @abstractmethod
    async def check_response(self, response: str) -> bool:
        """Check if the answer is correct."""
        raise NotImplementedError

    def embed(self, level: "Level", question_index: int) -> Embed:
        """Return an embed message for the question."""
        return Embed(
            title=f"{level.name}: {level.topic}",
            description=f"## Question {question_index}\n{self.question}",
            color=discord.Color.blurple(),
        )

    def view(self) -> "QuestionView":
        """Return the view for the question."""
        return QuestionView(self)


class QuestionStatus(Enum):
    """Status of the question interaction."""

    IN_PROGRESS = auto()
    CORRECT = auto()
    INCORRECT = auto()
    EXITED = auto()


class QuestionView(View):
    """View for a question.

    The view contains buttons for the user to interact with the question.
    """

    def __init__(self, question: Question) -> None:
        super().__init__()
        self.question = question
        self.next_question_interaction: Interaction | None = None
        self.status: QuestionStatus = QuestionStatus.IN_PROGRESS

    @discord.ui.button(
        label="Show hints",
        style=discord.ButtonStyle.secondary,
    )
    async def show_hints(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Show the hints for the question."""
        await interaction.response.send_message(content="\n".join(self.question.hints))

    @discord.ui.button(
        label="Correct answer",
        style=discord.ButtonStyle.success,
    )
    async def correct_answer(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Correct answer button."""
        self.next_question_interaction = interaction
        self.status = QuestionStatus.CORRECT
        self.stop()

    @discord.ui.button(
        label="Incorrect answer",
        style=discord.ButtonStyle.danger,
    )
    async def incorrect_answer(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Incorrect answer button."""
        self.next_question_interaction = interaction
        self.status = QuestionStatus.INCORRECT
        self.stop()

    @discord.ui.button(
        label="Quit",
        style=discord.ButtonStyle.danger,
    )
    async def quit_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Quit the question."""
        self.next_question_interaction = interaction
        self.status = QuestionStatus.EXITED
        self.stop()


class MultipleChoiceQuestion(Question):
    """A type of Level where the user selects the correct answer from multiple choices.

    In the JSON data for a multiple choice question, the following additional fields must be included:
    {
        "options": {
            "a": "4",
            "b": "5",
            "c": "6",
        },
        "answer": "a",
    }

    The `options` field is a dictionary where the keys are the options and the values are the value of the option.
    The keys should be single lowercase letters, starting from "A" and increasing alphabetically and serves as the
    ID for the option.

    The `answer` field is a string that contains the ID of the correct answer. The ID should be one of the keys in the
    `options` dictionary.
    """

    def __init__(self, question: str, hints: list[str], options: dict[str, str], answer: str) -> None:
        self.type = "multiple_choice"
        self.question = question
        self.hints = hints
        self.options = options
        self.answer = answer

    async def check_response(self, response: str) -> bool:  # noqa: D102
        return response == self.answer


class WriteCodeQuestion(Question):
    """A type of Level where the user writes code to solve a problem.

    In the JSON data for a write code question, the following additional fields must be included:
    {
        "test_cases": [
            ["add(1, 2)", "3"],
            ["add(-1, 3)", "2"],
        ],
    }

    The `test_cases` field is a list of tuples where the first element is the input to a unit test and the second
    is the expected output. The input and output should be strings that can be evaluated as Python code. For example,
    if the expected value is the string literal 'hello', it should be enclosed in quotes: "'hello'".

    The question should clearly state what the expected name of the function to be created is. For example, if the
    question is to create a function that adds two numbers, the question should state that the function should be
    named `add`. If the function is not named correctly, the tests will fail.
    """

    def __init__(self, question: str, hints: list[str], test_cases: list[dict[str, str]]) -> None:
        self.type = "write_code"
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
        test_strings = []
        for test_case in self.test_cases:
            input = test_case["input"]
            output = test_case["output"]
            test_strings.append(self._get_assert_equal_string(input, output))
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
    question_type = question_data.get("type")
    question_data.pop("type")
    match question_type:
        case "multiple_choice":
            return MultipleChoiceQuestion(**question_data)
        case "write_code":
            return WriteCodeQuestion(**question_data)
        case _:
            raise ValueError
