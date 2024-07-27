from __future__ import annotations

from typing import Protocol

from database.database import Score as ScoreRepo


class ScoreDB(Protocol):
    """Template for Scores  database."""

    def fetch_scores(self) -> list:
        """Fetch scores method."""


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
        return self.level == other.level and self.username == other.username and self.score == other.score

    def __hash__(self) -> None:
        return hash((self.username, self.level))

    def __repr__(self) -> str:
        return f"Score<level={self.level} username={self.username} score={self.score}>"


class ScoreSheet:
    """Scoresheet for `level`."""

    def __init__(self, db: ScoreDB, level: int) -> None:
        self.level = level
        self._sheet: list[Score] = self.load_from_database(db)

    def __iter__(self) -> list[Score]:
        return (score for score in sorted(self._sheet))

    def __len__(self) -> int:
        return len(self._sheet)

    def __repr__(self) -> str:
        return f"ScoreSheet<level={self.level}>"

    def load_from_database(self, db: ScoreDB | None) -> list[Score]:
        """Fetch all scores info for a particular level from database."""
        db = db or ScoreRepo()
        return [Score(**row) for row in db.fetch_scores(level=self.level)]

    def add(self, username: str, score: int) -> None:
        """Add user score to scoresheet."""
        # create score object
        score_obj = Score(level=self.level, username=username, score=score)

        # if user already has a record on the scoresheet
        # update the record
        if score_obj in self._sheet:
            self.update(score_obj)
        else:
            self._sheet.append(score_obj)

    def get(self, username: str) -> Score:
        """Return the index for user's score."""
        for score in self._sheet:
            if score.username == username:
                return score
        return None

    def remove(self, username: str) -> None:
        """Remove username from level score sheet."""
        score = self.get(username)
        if score:
            self._sheet.remove(score)

    def _update(self, score_obj: Score, score: int) -> None:
        """Update user score.

        Perform update only if user's new score is greater than the currently recorded score.
        """
        if score_obj <= score:
            return

        index = self._sheet.index(score_obj)
        self._sheet[index].score = score

        # sort scoresheet
        self._sheet.sort()

    def sort(self) -> list[Score]:
        """Sort score sheet."""
        return sorted(self, reverse=True)
