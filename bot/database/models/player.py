from __future__ import annotations

from typing import NamedTuple, Protocol

from database.database import PlayerDetail

LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
SPECIAL_LEVELS = [12, 13, 14]
MAX_LEVEL = 11  # Last level on the standard path of the game


class Position(NamedTuple):
    """Holds coordinates Of User."""

    x: int
    y: int


class PlayerDB(Protocol):
    """Template for player database."""

    def get(self, username: str) -> list:
        """Return player details."""

    def insert(self, username: str, level: int, status: str, score: int) -> None:
        """Insert into player table."""


class PlayDetail:
    """Class model for play session."""

    def __init__(
        self,
        username: str,
        level: int,
        score: int,
        *,
        available: bool = True,
        completed: bool = True,
    ) -> None:
        self.username = username
        self.level = level
        self.score = score
        self.available = available
        self.completed = completed

    def __eq__(self, other: PlayDetail) -> bool:
        return self.username == other.username and self.level == other.level and self.completed == other.completed

    def __hash__(self) -> int:
        return hash((self.username, self.level))

    def __gt__(self, other: PlayDetail) -> bool:
        if self.level == other.level:
            return self.score > other.score
        return LEVELS.index(self.level) > LEVELS.index(other.level)

    def __ge__(self, other: PlayDetail) -> bool:
        if self.level == other.level:
            return self.score >= other.score
        return LEVELS.index(self.level) >= LEVELS.index(other.level)

    @property
    def level_value(self) -> int | str:
        """Return player level.

        All levels are internally stored as integers (1-14).
        """
        return self.level

    def as_dict(self) -> dict:
        """Represent play object as dictionary."""
        return {"username": self.username, "level": self.level, "score": self.score, "completed": self.completed}

    def summary(self) -> dict:
        """Summary of play."""
        return {
            "lvl_id": self.level,
            "available": self.available,
            "completed": self.completed,
        }

    def is_special(self) -> bool:
        """Check if play is for a special level."""
        return self.level in SPECIAL_LEVELS


class PlayHistory(list):
    """Collection of PlayDetails."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN003 ANN002
        username = kwargs.pop("username")
        super().__init__(*args, **kwargs)
        self.new_plays = []
        self.username = username

    def __contains__(self, item: str | PlayDetail) -> bool:
        if isinstance(item, str) and item.startswith("lvl"):
            level = item[3:]  # Remove leading 'lvl'
            level = int(level)
            return bool(any(play.level_value == level for play in self))

        return super().__contains__(item)

    def __getitem__(self, index: int | str | slice) -> PlayDetail | list[PlayDetail]:
        """Allow dynamic access to play history.

        Enables indexing by valid string or slice of string
        >>> playhistory['lvl6'] # return plays with level == 6
        >>> playhistory['lvl5' : 'lvl7'] # return plays with levels in [5,6,7]
        >>> playhistory['lvl7' : 'lvl2'] # returns an empty playhistory
        >>> playhistory[0] # normal indexing
        """
        if isinstance(index, str):
            if index.startswith("lvl"):
                level = index[3:]  # Remove leading 'lvl'
                level = int(level)
                return self.get_plays_by_level(level)
            error = f"Invalid string value: {index}"
            raise ValueError(error)

        if isinstance(index, slice):
            start, stop = index.start, index.stop
            if isinstance(start, str) and isinstance(stop, str):
                if start.startswith("lvl") and stop.startswith("lvl"):
                    start = int(start[3:])  # Remove leading 'lvl'
                    stop = int(stop[3:])  # Remove leading 'lvl'
                    return self.get_plays_by_level(start=start, stop=stop)
                error = "Invalid string slice object : {index}. Use slice(lvlid, lvlid)"
                raise ValueError(error)

        return super().__getitem__(index)

    def get_plays_by_level(self, start: int, stop: int | None = None) -> PlayHistory:
        """Return plays for a given level or within a range of levels."""
        if stop is None:
            return self.__class__([play for play in self if play.level_value == start], username=self.username)

        level_range = list(range(start, stop + 1))
        return self.__class__(
            sorted([play for play in self if play.level_value in level_range]),
            username=self.username,
        )

    @property
    def max_level_played(self) -> PlayDetail:
        """Return player's max level.

        Special levels not included.
        """
        normal_level_played = [play for play in self if not play.is_special()]
        if normal_level_played:
            return max(normal_level_played)
        return PlayDetail(username=self.username, level=1, score=0, completed=False)

    def append(self, item: PlayDetail) -> None:
        """Save additions as new play before adding to history."""
        self.new_plays.append(item)
        super().append(item)

    def summary(self, *, completed: bool = False) -> list[dict]:
        """Return summary of play history."""
        if completed:
            return [play.summary() for play in sorted(set(self)) if play.completed]
        return [play.summary() for play in sorted(set(self))]


class Player:
    """Object model for player."""

    def __init__(self, username: str, details: list, coord: tuple | None = None) -> None:
        self.username = username
        self.history = PlayHistory([PlayDetail(**record) for record in details], username=username)
        self.position = Position(*coord) if coord else Position(0, 0)

    def __repr__(self) -> str:
        return f"Player<username={self.username} @ {self.position}>"

    @property
    def max_level(self) -> int:
        """Returns max level."""
        return self.history.max_level_played.level if self.history else 0

    @property
    def next_level(self) -> int:
        """Returns next level."""
        # current level is the max played level
        play = self.history.max_level_played
        if not play.completed:
            return play.level
        return play.level if play.level == MAX_LEVEL else play.level + 1

    @property
    def summary(self) -> list[dict]:
        """Return player summary as a dictionary."""
        # Available levels is a list of:
        # - completed level
        # - player's next level
        # - special levels unlocked

        # get completed levels
        summary = self.history.summary(completed=True)

        # include next level
        summary.append(
            {
                "lvl_id": self.next_level,
                "available": True,
                "completed": False,
            },
        )

        # If summary does not include completed special levels, add uncompleted but available special levels
        special_levels = set(self.history.get_plays_by_level(start=12, stop=14))
        for special in special_levels:
            if special.completed:
                continue
            summary.append(special.summary())

        return summary

    @property
    def new_data(self) -> list[dict]:
        """Returns data added to history but not in database."""
        if not self.history:
            return [{"username": self.username, "level": 1, "score": 0, "completed": False}]
        return [play.as_dict() for play in self.history.new_plays]

    def unlock_level(self, level: int) -> None:
        """Unlock level for player."""
        if (plays := self.history.get_plays_by_level(level)) and not any(filter(lambda play: play.available, plays)):
            print(f"Level {level} is already unlocked")
            return  # Level is already unlocked
        play = PlayDetail(username=self.username, level=level, score=0, available=True, completed=False)
        self.history.append(play)

    def complete_level(self, level: int, score: int) -> None:
        """Mark level as completed."""
        play = PlayDetail(username=self.username, level=level, score=score, completed=True)
        self.history.append(play)

    def set_position(self, x: int, y: int) -> None:
        """Set player position."""
        self.position = Position(x, y)

    def get_position(self) -> Position:
        """Return player position."""
        return self.position


class PlayerRepo:
    """Handles interaction between database and python models."""

    def __init__(self, db: PlayerDB | None = None) -> None:
        self.db = db or PlayerDetail()

    def get(self, username: str) -> Player:
        """Get player detail from database."""
        details = self.db.get(username)
        coordinate = self.db.get_map_coordinates(username)
        return Player(username, details, coordinate)

    def save(self, player: Player) -> None:
        """Save player detail to database."""
        data = player.new_data
        if data:
            data = tuple(data)
            self.db.insert_many(data)
            # clear new_data after saving
            player.new_data.clear()

        coord_x, coord_y = player.get_position()
        self.db.update_map_coordinates(player.username, coord_x, coord_y)
