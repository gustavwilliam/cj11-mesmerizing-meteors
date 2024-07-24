from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from levels import Level


class Controller:
    """Manage levels and run them when requested."""

    def __init__(self) -> None:
        self.levels = {}

    def add_level(self, level: "Level") -> None:
        """Add a level to the controller.

        Raises a ValueError if a level with the same id or map position already exists.
        """
        if level.id in self.levels:
            raise ValueError
        if level.map_position in [level.map_position for level in self.levels.values()]:
            raise ValueError
        self.levels[level.id] = level

    def get_level(self, position: tuple[int, int]) -> "Level":
        """Get the level at a given map position.

        Raises a ValueError if no level is found at the given position.
        """
        for level in self.levels.values():
            if level.map_position == position:
                return level
        raise ValueError
