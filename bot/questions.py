import re
import typing
from abc import abstractmethod
from enum import Enum, auto
from typing import Protocol

import discord
from config import Emoji
from discord import Embed, Interaction, TextStyle
from utils.eval import eval_python
from utils.view import UserOnlyView

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
    unlocked_hints: int  # Indexes of unlocked hints

    def __str__(self) -> str:
        """Return the question text."""
        return self.question

    @abstractmethod
    async def check_response(self, response: str) -> bool:
        """Check if the answer is correct."""
        raise NotImplementedError

    def get_embed_description(self, question_index: int) -> str:
        """Return the description for the embed message."""
        return f"## Question {question_index}\n{self.question}"

    def embed(self, level: "Level", question_index: int) -> Embed:
        """Return an embed message for the question."""
        embed = Embed(
            title=f"{level.name}: {level.topic}",
            description=self.get_embed_description(question_index),
            color=discord.Color.blurple(),
        )
        embed.set_thumbnail(
            url="attachment://hearts.png",
        )  # Must be exactly hearts.png. Level.get_hearts_file depends on it
        return embed

    def view(self, user: discord.User | discord.Member) -> "QuestionView":
        """Return the view for the question."""
        if self.type == "multiple_choice":
            return MultipleChoiceQuestionView(self, user)  # type: ignore  # noqa: PGH003
        if self.type in ["write_code", "write_golf_code"]:
            return WriteCodeQuestionView(self, user)  # type: ignore  # noqa: PGH003
        raise ValueError


class QuestionStatus(Enum):
    """Status of the question interaction."""

    IN_PROGRESS = auto()
    CORRECT = auto()
    INCORRECT = auto()
    EXITED = auto()


class QuestionView(UserOnlyView):
    """View for a question.

    The view contains buttons for the user to interact with the question.
    """

    def __init__(self, question: Question, user: discord.User | discord.Member) -> None:
        super().__init__(original_user=user)
        self.question = question
        self.next_question_interaction: Interaction | None = None
        self.status: QuestionStatus = QuestionStatus.IN_PROGRESS

    @discord.ui.button(
        emoji=discord.PartialEmoji.from_str(Emoji.HINT.value),
        label="Hint",
        row=2,
        style=discord.ButtonStyle.secondary,
    )
    async def get_a_hint(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Reveal one more hint."""
        if self.question.unlocked_hints < len(self.question.hints):
            self.question.unlocked_hints += 1
        hints = "- " + "\n- ".join(self.question.hints[: self.question.unlocked_hints])
        await interaction.response.send_message(
            content=f"### Hints ({self.question.unlocked_hints}/{len(self.question.hints)})\n" + hints,
            ephemeral=True,
        )

    @discord.ui.button(
        label="Quit level",
        emoji=discord.PartialEmoji.from_str(Emoji.CROSS.value),
        style=discord.ButtonStyle.secondary,
        row=2,
    )
    async def quit_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Quit the question."""
        await interaction.response.defer()
        await self.on_quit(interaction)

    async def on_quit(self, interaction: discord.Interaction) -> None:
        """Execute when the user quits the question."""
        self.status = QuestionStatus.EXITED
        self.next_question_interaction = interaction
        self.stop()

    async def on_success(self, interaction: discord.Interaction) -> None:
        """Execute when the user answers the question correctly."""
        self.status = QuestionStatus.CORRECT
        self.next_question_interaction = interaction
        self.stop()

    async def on_fail(self, interaction: discord.Interaction) -> None:
        """Execute when the user answers the question incorrectly."""
        self.status = QuestionStatus.INCORRECT
        self.next_question_interaction = interaction
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
        self.unlocked_hints = 0
        self.options = options
        self.answer = answer

    async def check_response(self, response: str) -> bool:  # noqa: D102
        return response == self.answer


class MultipleChoiceQuestionView(QuestionView):
    """View for a multiple choice question.

    The view contains buttons for the user to select the answer.
    """

    def __init__(self, question: MultipleChoiceQuestion, user: discord.User | discord.Member) -> None:
        super().__init__(question, user)
        self.question = question
        for option_id, label in question.options.items():
            self.add_option_button(option_id, label)

    @staticmethod
    def _emoji(option_id: str) -> discord.PartialEmoji:
        ids = {
            "a": Emoji.LETTER_A,
            "b": Emoji.LETTER_B,
            "c": Emoji.LETTER_C,
            "d": Emoji.LETTER_D,
            "e": Emoji.LETTER_E,
            "f": Emoji.LETTER_F,
        }
        return discord.PartialEmoji.from_str(
            ids[option_id].value,
        )

    def add_option_button(self, option_id: str, label: str) -> None:
        """Add a button for an option."""

        async def callback(interaction: discord.Interaction) -> None:
            """Button callback."""
            await interaction.response.defer()
            if await self.question.check_response(option_id):
                await self.on_success(interaction)
            else:
                await self.on_fail(interaction)

        button = discord.ui.Button(
            emoji=self._emoji(option_id),
            label=label,
            style=discord.ButtonStyle.primary,
        )
        button.callback = callback
        self.add_item(button)


class WriteCodeQuestion(Question):
    """A type of Level where the user writes code to solve a problem.

    In the JSON data for a write code question, the following additional fields must be included:
    {
        "pre_code": "squares = ",  # Assign user's one-liner to variable squares
        "test_cases": [
            ["add(1, 2)", "3"],
            ["add(-1, 3)", "2"],
        ],
    }

    The `test_cases` field is a list of tuples where the first element is the input to a unit test and the second
    is the expected output. The input and output should be strings that can be evaluated as Python code. For example,
    if the expected value is the string literal 'hello', it should be enclosed in quotes: "'hello'".

    The `pre_code` code will be insert right before the user's code. No newline will be inserted between it and the
    user's code, which enables assigning the user's code output to a variable. If you do want to separate the pre_code
    from the user's code, please end pre_code with a line break (\\n). For example: `"pre_code": "import inspect\\n"`.
    `pre_code` is an optional field.

    The question should clearly state what the expected name of the function to be created is. For example, if the
    question is to create a function that adds two numbers, the question should state that the function should be
    named `add`. If the function is not named correctly, the tests will fail.
    """

    def __init__(
        self,
        question: str,
        hints: list[str],
        test_cases: list[dict[str, str]],
        pre_code: str | None = None,
        pre_submit_code: str | None = None,
    ) -> None:
        self.type = "write_code"
        self.question = question
        self.hints = hints
        self.pre_code = pre_code
        self.unlocked_hints = 0
        self.pre_submit_code = pre_submit_code
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
            + ("" if self.pre_code is None else self.pre_code + "\n")  # Adds code to run before user code
            + (
                "" if self.pre_submit_code is None else self.pre_submit_code
            )  # Code to collect user output from one-liner, without a line break after it
            + user_code.expandtabs(2)  # Insert user code. Tabs -> spaces for consistency with test code
            + "\nclass Test(unittest.TestCase):\n"  # Setup test class
            + " def test_cases(self):"  # Setup test method
            + "\n  "  # Indentation for first test case
            + "\n  ".join(test_strings)  # Add assertions for test cases
            + "\nunittest.main()"  # Run unit tests
        )

    def get_embed_description(self, question_index: int) -> str:  # noqa: D102
        return (
            super().get_embed_description(question_index)
            + "\n\n*Tip: press the Code Playground button to try out your code before submitting!*"
            + " :warning: *But there and **ONLY THERE** you will need to use `print(...)` to see the result*"
        )


class WriteGolfCodeQuestion(WriteCodeQuestion):
    """A type of Level where the user writes code to solve a problem in the fewest characters possible."""

    def __init__(  # noqa: PLR0913, RUF100
        self,
        question: str,
        hints: list[str],
        test_cases: list[dict[str, str]],
        max_characters: int,
        pre_code: str | None = None,
        pre_submit_code: str | None = None,
    ) -> None:
        self.type = "write_code"
        self.question = question
        self.hints = hints
        self.pre_submit_code = pre_submit_code
        self.unlocked_hints = 0
        self.pre_code = pre_code
        self.max_characters = max_characters
        self.test_cases = test_cases

    async def check_response(self, code: str) -> bool:
        """Check if the code answer is correct.

        Runs a suite of unit tests on the code. If they all pass, the code is deemed correct.

        Raises an error if a connection to the code evaluation service fails.
        """
        test_string = self._get_test_string(code)
        output = await eval_python(test_string)
        passes_tests = bool(check_test.search(output))
        return passes_tests and len(code) <= self.max_characters

    def get_embed_description(self, question_index: int) -> str:  # noqa: D102
        return (
            super(WriteCodeQuestion, self).get_embed_description(question_index)
            + f"\n### Maximum characters allowed: {self.max_characters}\n"
            + "\n*Tip: press the Code Playground button to try out your code before submitting!*"
        )


class CodeModal(discord.ui.Modal, title="Submit code"):
    """Modal for submitting code."""

    def __init__(self, *args, view: "WriteCodeQuestionView", title: str | None = None, **kwargs) -> None:  # noqa: ANN002, ANN003
        super().__init__(*args, **kwargs)
        self.view = view
        self.submit_interaction = None
        if title is not None:
            self.title = title

    code_input = discord.ui.TextInput(
        label="Python Code",
        placeholder="Write your code here",
        style=TextStyle.long,
        min_length=1,
        max_length=2000,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Submit the code."""
        self.submit_interaction = interaction
        self.stop()


class WriteCodeQuestionView(QuestionView):
    """View for a write code question.

    The view contains a text box for the user to write code.
    """

    def __init__(self, question: WriteCodeQuestion, user: discord.User | discord.Member) -> None:
        super().__init__(question, user)
        self.question = question
        self.post_modal_interaction: Interaction

    @discord.ui.button(
        label="Enter Python code",
        style=discord.ButtonStyle.primary,
    )
    async def submit_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Open modal and get text response."""
        modal = CodeModal(view=self)
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.submit_interaction is None:
            self.status = QuestionStatus.EXITED
            print("Unable to get interaction, exiting question.")
            self.stop()
            return
        await modal.submit_interaction.response.defer()
        if await self.question.check_response(modal.code_input.value):
            await self.on_success(modal.submit_interaction)
        else:
            await self.on_fail(modal.submit_interaction)

    @discord.ui.button(
        label="Code Playground",
        style=discord.ButtonStyle.primary,
    )
    async def playground_button(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Open code playground modal."""
        modal = CodeModal(view=self, title="Test you code")
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.submit_interaction is None:
            await interaction.response.send_message(
                content="Unable to run code right now. Please try again later.",
                ephemeral=True,
            )
            return

        await modal.submit_interaction.response.defer(thinking=True, ephemeral=True)
        code_input = (self.question.pre_code or "") + "\n" + modal.code_input.value
        output = await eval_python(code_input)
        output = output[:1900] if len(output) > 0 and output != "\n" else "No output"
        embed = Embed(
            title="Code Playground Results",
            description=f"**Input:**\n```py\n{code_input}\n```\n**Output:**\n```py\n{output}\n```",
            color=discord.Color.blurple(),
        )
        await modal.submit_interaction.followup.send(
            embed=embed,
            ephemeral=True,
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
        case "write_golf_code":
            return WriteGolfCodeQuestion(**question_data)
        case _:
            raise ValueError
