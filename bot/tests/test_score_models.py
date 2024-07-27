import unittest

from database.models import Score, ScoreSheet


class TestDB:
    """Fake Score repository."""

    def __init__(self) -> None:
        self.store = []

    def add(self, level: int, username: str, score: int) -> None:
        """Add user to score board."""
        kwargs = {"username": username, "level": level, "score": score}
        self.store.append(kwargs)

    def fetch_scores(self, level: int) -> list[Score]:
        """Fetch users from repository."""
        return [score for score in self.store if score["level"] == level]

    def _get(self, kwargs: dict) -> int:
        """Get user index."""
        for index, score in enumerate(self.store):
            if all((score[k] == kwargs[k]) for k in kwargs):
                return index
        return None

    def get(self, level: int, username: str, score: int | None = None) -> Score:
        """Get user detail."""
        kwargs = {"level": level, "username": username}
        if score:
            kwargs["score"] = score
        index = self._get(kwargs)
        if index:
            return self.store[index]
        return None

    def update(self, level: int, username: str, score: int) -> None:
        """Update user score."""
        kwargs = {"level": level, "username": username}
        index = self._get(kwargs)
        if index:
            self.store[index]["score"] = score

    def remove(self, level: int, username: str) -> None:
        """Remove user."""
        kwargs = {"level": level, "username": username}
        index = self._get(kwargs)
        if index:
            self.store.pop(index)


class TestModels(unittest.TestCase):
    """Test class for models."""

    def populate_db(self) -> TestDB:
        """Populate fake database with dummy data."""
        test_db = TestDB()
        test_db.add(username="noble", level=1, score=100)
        test_db.add(username="dejavu", level=2, score=125)
        test_db.add(username="jasper", level=2, score=150)
        test_db.add(username="heavenmercy", level=3, score=250)
        test_db.add(username="verstergurkan", level=3, score=225)
        return test_db

    def test_scoresheet_level(self) -> None:
        """Test level property.

        Check if the score row in scoresheet
        object are those that belong to its
        level.
        """
        test_db = self.populate_db()
        rows = 2
        scoresheet = ScoreSheet(db=test_db, level=2)
        assert len(scoresheet) == rows

    def test_score_in_scoresheet(self) -> None:
        """Test score in scoresheet.

        Check that a specific score is in scoresheet.
        """
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=2)
        score_obj = Score(username="dejavu", level=2, score=125)
        assert score_obj in scoresheet

    def test_scoresheet_sorted(self) -> None:
        """Test sort method."""
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=2)
        ordered_score_list = [
            Score(username="jasper", level=2, score=150),
            Score(username="dejavu", level=2, score=125),
        ]

        scoresheet_list = scoresheet.sort()
        assert ordered_score_list == scoresheet_list

    """
    scoresheet only fetch from database table
    def test_scoresheet_add_saves_to_database(self) -> None:
        "Test scoresheet syncs with database."
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=2)
        scoresheet.add(username="noble", score=100)
        assert test_db.get(username="noble", score=100, level=2) is not None
    """

    """
    def test_update_scoresheet(self) -> None:
        "Test update method."
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=3)
        score = 300
        scoresheet.update(username="heavenmercy", score=score)

        # check scoresheet
        score_obj = scoresheet.get("heavenmercy")
        assert score_obj.score == score

        # check database
        row = test_db.get(username="heavenmercy", level=3)
        assert row["score"] == score
    """

    def test_remove_score_from_scoresheet(self) -> None:
        """Test remove method."""
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=1)
        score_obj = scoresheet.get(username="noble")
        scoresheet.remove(username="noble")
        assert score_obj not in scoresheet


if __name__ == "__main__":
    unittest.main()
