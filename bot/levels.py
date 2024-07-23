from abc import abstractmethod
from typing import Protocol

from bot.controller import Controller


class Level(Protocol):
    """Protocol that all levels must implement.

    Different level types can be created by subclassing this protocol.

    Instances of the levels that subclass this protocol are created
    when a level is run. The data for the level is stored in the instance,
    for example, the score of the specific run. When the run is over,
    the instance is destroyed, so all data that should persist between runs
    should be stored in a different place.
    """

    controller: Controller
    id: str
    name: str
    description: str
    map_position: tuple[int, int]

    def __init__(self) -> None:
        """Register the level to the controller."""
        self.controller.add_level(self)

    @abstractmethod
    def run(self) -> None:
        """Run the level."""
        raise NotImplementedError

    def on_failure(self) -> None:
        """Call when the player fails the level."""
        print(self.name + " failed")  # Default implementation

    def on_success(self) -> None:
        """Call when the player succeeds the level."""
        print(self.name + " succeeded")  # Default implementation


class EvaluateCodeLevel(Level):
    """A type of Level where the user figures out the output of a code snippet."""


class MultipleChoiceLevel(Level):
    """A type of Level where the user selects the correct answer from multiple choices."""


class WriteCodeLevel(Level):
    """A type of Level where the user writes code to solve a problem."""
