import sqlite3
from pathlib import Path

PATH = Path(__file__).parent  # Path of the database


class Database:
    """Class that handles interactions with the database."""

    def __init__(self) -> None:

        # Default name of the database
        self.name = PATH.joinpath(".store.db")

        # Connection to the database
        self.__connection = sqlite3.connect(self.name)
        self.__cursor = self.__connection.cursor()

    def execute_command(self, command: str, data: tuple = ()) -> bool:
        """Execute the given command."""
        if self.__cursor.execute(command, data):
            self.__connection.commit()  # Commit the changes to the DB
            return True
        return False

    def disconnect(self) -> bool:
        """Close the database connection."""
        return not bool(self.__connection.close())

    def __str__(self) -> str:
        return f"Database name: {self.name}"


class Score(Database):
    """Class that handles interactions with the Score table."""

    def __init__(self) -> None:
        super().__init__()

        command = """CREATE TABLE IF NOT EXISTS Score (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NON NULL,
                score INTEGER NON NULL)"""
        super().execute_command(command)

    def add_score(self, username: str, score: int) -> bool:
        """Add a score in the Score table."""

        command = "INSERT INTO Score (username, score) VALUES(?, ?)"
        return bool(self.execute_command(command, (username, score)))

    def remove_score(self, username: str) -> bool:
        """Remove a score in the Score table."""

        command = "DELETE FROM Score WHERE username = ?"
        return bool(self.execute_command(command, (username,)))


class Quiz(Database):
    """Class that handles interactions with the Quizzes in the QUiz table."""

    def __init__(self) -> None:
        super().__init__()

        command = """CREATE TABLE IF NOT EXISTS Quiz (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level INTEGER NON NULL,
                question TEXT NON NULL,
                answer TEXT NON NULL,
                lesson TEXT NON NULL)"""
        super().execute_command(command)

    def add_quiz(self, level: int, question: str, answer: str, lesson: str) -> bool:
        """Add a quiz in the Quiz table."""

        command = """INSERT INTO Quiz (level, question, answer, lesson)
        VALUES(?, ?, ?, ?)"""
        return bool(self.execute_command(command, (level, question, answer, lesson)))

    def remove_quiz(self, id: int) -> bool:
        """Remove a quiz in the Quiz table."""

        command = "DELETE FROM Quiz WHERE id = ?"
        return bool(self.execute_command(command, (id,)))

