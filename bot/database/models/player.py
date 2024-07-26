from __future__ import annotations

from typing import Protocol

from database.database import PlayerDetail

LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, "A", "B", "C"]
SPECIAL_LEVELS = ["A", "B", "C"]
THRESHOLD_SCORE = 1
MAX_LEVEL = 11


class PlayerDB(Protocol):
    """Template for player database."""

    def get(self, username: str) -> list:
        """Return player details."""

    def insert(self, username: str, level: int, status: str, score: int) -> None:
        """Insert into player table."""


class PlayDetail:
    """Class model for play session."""

    def __init__(  # noqa: PLR0913
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
        return self.username == other.username and self.level == other.level

    def __hash__(self) -> int:
        return hash((self.username, self.level))

    def __gt__(self, other: PlayDetail) -> bool:
        if self.level == other.level:
            return self.score > other.score
        return LEVELS.index(self.level) > LEVELS.index(other.level)

    def __ge__(self, other: PlayDetail) -> bool:
        if self.level == other.level:
            return self.score >= other.score
        return LEVELS.index(self.level) > LEVELS.index(other.level)

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

    def is_special(self) -> True:
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
            level = item[3:]
            level = level if level in SPECIAL_LEVELS else int(level)
            return bool(any(play.level == level for play in self))

        return super().__contains__(item)

    def __getitem__(self, index: int | str | slice) -> PlayDetail | list[PlayDetail]:
        """Allow dynamic access to play history.

        Enables indexing by valid string or slice of string
        >>> playhistory['lvl6'] # return plays with level == 6
        >>> playhistory['lvl5' : 'lvl7'] # return plays with levels in [5,6,7]
        >>> playhistory['lvl7' : 'lvl2'] # returns an empty playhistory
        >>> playhistory[0] # normal indexing
        >>> playhistory['lvlA' : 'lvlC'] # currently doesn't work!!!, would raise an Exception
        """
        if isinstance(index, str):
            if index.startswith("lvl"):
                level = index[3:]
                level = level if level in SPECIAL_LEVELS else int(level)
                return self._get_plays_by_level(level)
            error = f"Invalid string value: {index}"
            raise ValueError(error)

        if isinstance(index, slice):
            start, stop = index.start, index.stop
            if isinstance(start, str) and isinstance(stop, str):
                if start.startswith("lvl") and stop.startswith("lvl"):
                    start = int(start[3:])
                    stop = int(stop[3:])
                    return self._get_plays_by_level(start=start, stop=stop)
                error = "Invalid string slice object : {index}. Use slice(lvlid, lvlid)"
                raise ValueError(error)

        return super().__getitem__(index)

    def _get_plays_by_level(self, start: int | str, stop: int | None = None) -> PlayHistory:
        """Return plays for a given level or within a range of levels."""
        if stop is None:
            return self.__class__([play for play in self if play.level == start])

        level_range = list(range(start, stop + 1))
        return self.__class__(sorted([play for play in self if play.level in level_range]))

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

    def __init__(self, username: str, details: list) -> None:
        self.username = username
        self.history = PlayHistory([PlayDetail(**record) for record in details], username=username)

    def __repr__(self) -> str:
        return f"Player<username={self.username}>"

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
    def special_levels_unlocked(self) -> list:
        """Return special levels availabe to user."""
        unlocked_levels = []
        if "lvl4" in self.history:
            unlocked_levels.append("lvlA")
        if "lvl11" in self.history:
            unlocked_levels.append("lvl11")
        if "lvlB" in self.history and max(self.history["lvlB"]).score > THRESHOLD_SCORE:
            unlocked_levels.append("lvlC")

        return unlocked_levels

    @property
    def summary(self) -> dict:
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

        # include unlocked levels not yet completed
        for level in self.special_levels_unlocked:
            if level not in self.history:
                summary.append({"lvl_id": level, "available": True, "completed": False})

        return summary

    @property
    def new_data(self) -> dict:
        """Returns data added to history but not in database."""
        if not self.history:
            return [{"username": self.username, "level": 1, "score": 0, "completed": False}]
        return [play.as_dict() for play in self.history.new_plays]

    def complete_level(self, level: int, score: int) -> None:
        """Mark level as completed."""
        play = PlayDetail(username=self.username, level=level, score=score, completed=True)
        self.history.append(play)


class PlayerRepo:
    """Handles interaction between database and python models."""

    def __init__(self, db: PlayerDB | None = None) -> None:
        self.db = db or PlayerDetail()

    def get(self, username: str) -> Player:
        """Get player detail from database."""
        details = self.db.get(username)
        return Player(username, details)

    def save(self, player: Player) -> None:
        """Save player detail to database."""
        data = player.new_data
        if data:
            data = tuple(data)
            self.db.insert_many(data)
