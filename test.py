import unittest

from bot.database.database import Score
from bot.database.models import Score, ScoreSheet


class TestDB:
    def __init__(self):
        self.store = []

    def add(self, **kwargs):
        self.store.append(kwargs)

    def fetch(self, level):
        return [score for score in self.store if score['level'] == level]

    def _get(self, kwargs):
        index = 0
        for score in self.store:
            if all((score[k] == kwargs[k]) for k in kwargs.keys()):
                return index
            index += 1

    def get(self, **kwargs):
        index = self._get(kwargs)
        if index:
            return self.store[index]

    def update(self, **kwargs):
        score = kwargs.pop('score')
        index = self._get(kwargs)
        if index:
            self.store[index]['score'] = score

    def remove(self, **kwargs):
        index = self._get(kwargs)
        if index:
            self.store.pop(index)


class InMemoryDb(Score):
    pass


class TestModels(unittest.TestCase):

    def populate_db(self):
        test_db = TestDB()
        test_db.add(username="noble", level=1, score=100)
        test_db.add(username="dejavu", level=2, score=125)
        test_db.add(username="jasper", level=2, score=150)
        test_db.add(username="heavenmercy", level=3, score=250)
        test_db.add(username="verstergurkan", level=3, score=225)
        return test_db

    def test_scoresheet_level(self):
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=2)
        self.assertTrue(len(scoresheet) == 2)

    def test_score_in_scoresheet(self):
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=2)
        score_obj = Score(username="dejavu", level=2, score=125)
        self.assertTrue(score_obj in scoresheet)

    def test_scoresheet_sorted(self):
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=2)
        ordered_score_list = [
            Score(username="jasper", level=2, score=150),
            Score(username="dejavu", level=2, score=125)
        ]

        scoresheet_list = [score for score in scoresheet.sort()]
        self.assertTrue(ordered_score_list == scoresheet_list)

    def test_scoresheet_add_saves_to_database(self):
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=2)
        scoresheet.add(username="noble", score=100)
        assert test_db.get(username="noble", score=100, level=2) is not None

    def test_update_scoresheet(self):
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=3)
        scoresheet.update(username="heavenmercy", score=300)
        
        # check scoresheet
        score_obj = scoresheet.get("heavenmercy")
        self.assertTrue(score_obj.score == 300)
        
        # check database 
        row = test_db.get(username="heavenmercy", level=3)
        self.assertTrue(row['score'] == 300)

    def test_remove_score_from_scoresheet(self):
        test_db = self.populate_db()
        scoresheet = ScoreSheet(db=test_db, level=1)
        score_obj = scoresheet.get(username="noble")
        scoresheet.remove(username="noble")
        self.assertTrue(score_obj not in scoresheet)



if __name__ == "__main__":
    unittest.main()
