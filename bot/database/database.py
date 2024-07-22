from __future__ import annotations

import sqlite3
from pathlib import Path

PATH = Path(__file__).parent  # Path of the database


class Database:
    """Class that handles interactions with the database."""

    __table_name__ = None

    def __init__(self, name:str|None = None) -> None:
        # Default name of the database
        self.name = name or PATH.joinpath(".store.db")

        # Connection to the database
        self.__connection = sqlite3.connect(self.name)
        self.__connection.row_factory = sqlite3.Row
        self.__cursor = self.__connection.cursor()

    @property
    def connection(self) -> sqlite3.Connection:
        """Connection property of database."""
        return self.__connection

    @property
    def cursor(self) -> sqlite3.Cursor:
        """Cursor property of database."""
        return self.connection.cursor()

    def execute_command(self, command: str, data: tuple = ()) -> bool:
        """Execute the given command."""
        if self.cursor.execute(command, data):
            self.connection.commit()  # Commit the changes to the DB
            return True
        return False

    def disconnect(self) -> bool:
        """Close the database connection."""
        return not bool(self.connection.close())

    def __str__(self) -> str:
        db_str = f"Database <name:{self.name}"
        if self.__table_name__:
            db_str = db_str + f" table : {self.__table_name__}>"
        else:
            db_str += ">"
        return db_str


class Score(Database):
    """Class that handles interactions with the Score table."""

    __table_name__ = "Score"

    def __init__(self) -> None:
        super().__init__()

        command = """CREATE TABLE IF NOT EXISTS Score (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NON NULL,
                score INTEGER NON NULL,
                level INTEGER NON NULL
                )"""
        super().execute_command(command)

    def add(self, level: int, username: str, score: int) -> bool:
        """Add a score in the Score table."""
        command = "INSERT INTO Score (level, username, score) VALUES(?, ?, ?)"
        return bool(self.execute_command(command, (level, username, score)))

    def remove(self, level: int, username: str) -> bool:
        """Remove a score in the Score table."""
        command = "DELETE FROM Score WHERE username = ? AND level = ?"
        return bool(
            self.execute_command(command, (username, level)),
        )

    def update(self, level: int, username: str, score: int) -> bool:
        """Update score in Score table."""
        command = """
            UPDATE Score
            SET score = ?
            WHERE level = ?
            AND username = ?
        """
        return bool(self.execute_command(command, (score, level, username)))

    def fetch(self, level: int) -> list:
        """Fetch level scoresheet."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT username, score
                FROM Score
                WHERE level = ?
                ORDER BY score DESC
            """,
                (level,),
            )
            return cursor.fetchall()
