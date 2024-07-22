from __future__ import annotations

from typing import Protocol


class Repository(Protocol):
    """Template for database protocol class."""

    def add(self) -> None:
        """Add method."""

    def remove(self) -> None:
        """Remove method."""

    def update(self) -> None:
        """Update method."""


class Score:
    """Object wrapper for a row instance in score sheet."""

    def __init__(self, username: str, score: int, level: int) -> None:
        self.username = username
        self.score = score
        self.level = level

    def __gt__(self, other: Score) -> bool:
        return self.score > other.score

    def __ge__(self, other: Score) -> bool:
        return self.score >= other.score

    def __eq__(self, other: Score) -> bool:
        # duplicate username in a level are not allowed
        return self.level == other.level and self.username == other.username

    def __hash__(self) -> None:
        return hash((self.username,))

    def __repr__(self) -> str:
        return f"Score<level={self.level} username={self.username} score={self.score}>"


class ScoreSheet:
    """Scoresheet for `level`."""

    def __init__(self, db: Repository, level: int) -> None:  # db uses duck-typing
        self.db = db
        self.level = level
        self._scores: list[Score] = self.get_level_scores()

    def __iter__(self) -> list[Score]:
        return (score for score in self._scores)

    def __len__(self) -> int:
        return len(self._scores)

    def __repr__(self) -> str:
        return f"ScoreSheet<level={self.level}>"

    def get_level_scores(self) -> str:
        """Fetch all scores info for a particular level from database."""
        return [Score(**row) for row in self.db.fetch(level=self.level)]

    def add(self, username: str, score: int) -> None:
        """Add user score to scoresheet."""
        # create score object
        score_obj = Score(level=self.level, username=username, score=score)
        # try updating score table
        # append to scores list if score table is updated
        if score_obj in self._scores:
            message = "Username already on scoresheet"
            raise ValueError(message)
        self.db.add(level=score_obj.level, username=username, score=score)
        self._scores.append(score_obj)

    def get(self, username: str) -> Score:
        """Return the row for user."""
        for score in self._scores:
            if score.username == username:
                return score
        return None

    def remove(self, username: str) -> None:
        """Remove username from level score sheet."""
        score = self.get(username)
        if score:
            self.db.remove(username=score.username, level=score.level)
            self._scores.remove(score)

    def update(self, username: str, score: int) -> None:
        """Update user score."""
        score_obj = self.get(username)
        if score_obj is None:
            message = "Username not in score sheet"
            raise ValueError(message)
        self.db.update(level=score_obj.level, username=score_obj.username, score=score)
        score_obj.score = score

    def update_by(self, username: str, update_score: int) -> None:
        """Increase user score by `update_score`."""
        score_obj = self.get(username)
        if score_obj is None:
            message = "Username not in score sheet"
            raise ValueError(message)
        score = score_obj.score + update_score
        self.db.update(level=score_obj.level, username=score_obj.username, score=score)
        score_obj.score = score

    def sort(self) -> list[Score]:
        """Sort score sheet."""
        return sorted(self, reverse=True)
