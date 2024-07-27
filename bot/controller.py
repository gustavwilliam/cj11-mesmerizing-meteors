from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from levels import Level


class Controller:
    """Manage levels and run them when requested."""

    _instance = None
    levels: ClassVar[list[type["Level"]]] = []

    def __new__(cls, *args, **kwargs) -> "Controller":  # noqa: ANN002, ANN003
        """Create a singleton instance of the Controller.

        This allows the Levels to sign up directly to the Controller. Since there will only be one
        Controller instance in the program, the Levels can be sure that they are signing up to the
        correct Controller, without needeing to pass it as an argument.
        """
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def add_level(self, level: type["Level"]) -> None:
        """Add a level to the controller.

        Raises a ValueError if a level with the same id or map position already exists.
        """
        if level.id in self.levels:
            raise ValueError
        if level.map_position in [level.map_position for level in self.levels]:
            raise ValueError
        self.levels.append(level)

    def get_level(self, position: tuple[int, int]) -> type["Level"] | None:
        """Get the level at a given map position, or return None if no level exists."""
        for level in self.levels:
            if level.map_position == position:
                return level
        return None

    def get_level_by_id(self, id: int) -> type["Level"] | None:
        """Get the level with the given id, or return None if no level exists."""
        for level in self.levels:
            if level.id == id:
                return level
        return None

    def is_level(self, position: tuple[int, int]) -> bool:
        """Check if a level exists at the given map position."""
        return any(level.map_position == position for level in self.levels)
