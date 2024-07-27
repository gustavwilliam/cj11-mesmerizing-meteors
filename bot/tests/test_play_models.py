import unittest

from database.models import PlayDetail, Player


class TestDB:
    """Fake Player repository."""

    def __init__(self) -> None:
        self.db = []

    def get(self, username: str) -> Player:
        """Get player detail."""
        details = [row for row in self.db if row["username"] == username]
        return Player(username, details)

    def save(self, player: Player) -> None:
        """Append new play data."""
        data = player.new_data
        if data:
            for row in data:
                self.db.append(row)


def populate_db() -> TestDB:
    """Populate test db."""
    test_db = TestDB()
    data = [
        {"username": "noble", "level": 1, "score": 125},
        {"username": "noble", "level": 2, "score": 230},
        {"username": "noble", "level": 3, "score": 100},
        {"username": "noble", "level": 2, "score": 150},
        {"username": "noble", "level": 1, "score": 300},
    ]

    test_db.db.extend(data)

    return test_db


class TestModel(unittest.TestCase):
    """Test class for models.

    Tests to be carried out:
    - ensure that saving a player detail only adds the new plays and doesn't duplicate old plays
    - test player next_level property
    - test unlocked levels
    - ensure that `player.summary` return levels with the right data
    - test dynamic play history access
    - test saving a new user works
    """

    def test_level_access(self) -> None:
        """Test history access by level."""
        test_db = populate_db()
        player = test_db.get(username="noble")
        plays = player.history["lvl2"]
        expected_plays = [
            PlayDetail(username="noble", level=2, score=230),
            PlayDetail(username="noble", level=2, score=150),
        ]
        assert plays == expected_plays

    def test_save_player(self) -> None:
        """Test PlayHistory `new_plays`."""
        test_db = populate_db()
        player = test_db.get(username="noble")
        new_play = {"username": "noble", "level": 4, "score": 200, "completed": True}
        player.history.append(PlayDetail(**new_play))
        test_db.save(player)
        assert new_play in test_db.db

    def test_special_levels_unlocked(self) -> None:
        """Test Player `special_levels_unlocked` property."""
        test_db = populate_db()
        player = test_db.get(username="noble")
        new_play = {"username": "noble", "level": 4, "score": 200, "completed": True}
        player.history.append(PlayDetail(**new_play))
        special_level = "lvlA"
        assert special_level in player.special_levels_unlocked

    def test_player_summary(self) -> None:
        """Test Player summary method."""
        test_db = populate_db()
        player = test_db.get(username="noble")
        expected_summary = [
            {"lvl_id": 1, "available": True, "completed": True},
            {"lvl_id": 2, "available": True, "completed": True},
            {"lvl_id": 3, "available": True, "completed": True},
            {"lvl_id": 4, "available": True, "completed": False},
        ]
        assert player.summary == expected_summary

    def test_save_new_user(self) -> None:
        """Test save new user."""
        test_db = populate_db()
        new_player = test_db.get(username="doe")
        new_play = {"username": "doe", "level": 1, "score": 0, "completed": False}
        new_player.history.append(PlayDetail(**new_play))
        test_db.save(new_player)
        assert new_play in test_db.db

    def test_level_in_history(self) -> None:
        """Test history `__contains__`."""
        player = populate_db().get(username="noble")
        assert ("lvl2" in player.history) is True


if __name__ == "__main__":
    unittest.main()
