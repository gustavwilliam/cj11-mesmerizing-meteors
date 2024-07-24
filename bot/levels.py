import json
from pathlib import Path
from typing import Protocol

from controller import Controller
from questions import Question, question_factory

with Path.open(Path("bot/questions.json")) as f:
    all_questions = json.load(f)


class Level(Protocol):
    """Protocol that all levels must implement.

    Different level types can be created by subclassing this protocol.
    All levels must run `Level.register()` to register the level class with the controller.
    This should happen at startup.

    Instances of the levels that subclass this protocol are created
    when a level is run. The data for the level is stored in the instance,
    for example, the score of the specific run. When the run is over,
    the instance is destroyed, so all data that should persist between runs
    should be stored in a different place.
    """

    id: int
    name: str
    topic: str
    map_position: tuple[int, int]
    questions: list[Question]

    @classmethod
    def register(cls) -> None:
        """Register a Level class with the controller."""
        Controller().add_level(cls)

    def __init__(self) -> None:
        """Fetch the data for the level."""
        self.fetch_level_data()

    def __str__(self) -> str:
        return self.name

    def fetch_level_data(self) -> None:
        """Fetch the questions, answers, and other data for the level and assign to questions attribute.

        The data is retrieved from bot/questions.json. The id of the level in the JSON file
        must match the id attribute of the Level subclass for the information to be loaded.
        If no questions are found for the level, a ValueError is raised.
        """
        questions = all_questions.get(str(self.id))
        if questions is None:
            raise ValueError("No questions found for level " + str(self.id))
        self.questions = [question_factory(**question_data) for question_data in questions]

    def run(self) -> None:
        """Run the level."""

    def on_failure(self) -> None:
        """Call when the player fails the level."""
        print(self.name + " failed")  # Default implementation

    def on_success(self) -> None:
        """Call when the player succeeds the level."""
        print(self.name + " succeeded")  # Default implementation


class Level1(Level):  # noqa: D101
    id = 1
    name = "Level 1"
    topic = "List Comprehensions"
    map_position = (1, 0)


class Level2(Level):  # noqa: D101
    id = 2
    name = "Level 2"
    topic = "Generators"
    map_position = (3, 0)


class Level3(Level):  # noqa: D101
    id = 3
    name = "Level 3"
    topic = "Iterator"
    map_position = (5, 0)


class Level4(Level):  # noqa: D101
    id = 4
    name = "Level 4"
    topic = "Function overloading"
    map_position = (8, 0)


def register_all_levels() -> None:
    """Register all levels with the controller."""
    Level1.register()
    Level2.register()
    Level3.register()
    Level4.register()
