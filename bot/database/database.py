from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

PATH = Path(__file__).parent  # Path of the database

SCHEMA = """
    CREATE TABLE IF NOT EXISTS player_detail(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NON NULL,
        level INTEGER NON NULL DEFAULT 1,
        score INTEGER NON NULL DEFAULT 0,
        completed BOOLEAN NON NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS map(
        username TEXT PRIMARY KEY,
        coord_x INTEGER NON NULL,
        coord_y INTEGER NON NULL
    );
"""

sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))


class Database:
    """Class that handles interactions with the database."""

    __table_name__ = None

    def __init__(self, name: str | None = None) -> None:
        # Default name of the database
        self.name = name or PATH.joinpath(".store.db")

        # Connection to the database
        self.__connection = sqlite3.connect(self.name)
        self.__connection.row_factory = sqlite3.Row
        self.__cursor = self.__connection.cursor()

        # initialize database
        self.__cursor.executescript(SCHEMA)

    @property
    def connection(self) -> sqlite3.Connection:
        """Connection property of database."""
        return self.__connection

    @property
    def cursor(self) -> sqlite3.Cursor:
        """Cursor property of database."""
        return closing(self.connection.cursor())

    def execute_command(self, command: str, data: tuple = ()) -> bool:
        """Execute the given command."""
        cursor = self.connection.cursor()
        if cursor.execute(command, data):
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
    """SQL repository for scoresheet."""

    __table_name__ = "player_detail"

    def fetch(self, level: int) -> list:
        """Fetch level scoresheet."""
        with self.cursor as cursor:
            cursor.execute(
                """
                SELECT DISTINCT(username), score
                FROM player_detail
                WHERE level = ?
                ORDER BY score DESC
                """,
                (level,),
            )
            return cursor.fetchall()


class PlayerDetail(Database):
    """SQL repository for player details."""

    __table_name__ = "player_detail"

    def get(self, username: str) -> list:
        """Load player's details from player_detail table."""
        with self.cursor as cursor:
            cursor.execute(
                """
                SELECT username, level, score, completed
                FROM player_detail
                WHERE username = ?
                ORDER BY level ASC;
            """,
                (username,),
            )

            return cursor.fetchall()

    def insert(self, username: str, level: int, score: int, *, completed: bool = True) -> None:
        """Insert into player_detail."""
        command = """
            INSERT INTO player_detail (username, level, score, completed)
            VALUES (?, ?, ?, ?)
        """

        self.execute_command(command, (username, level, score, completed))

    def insert_many(self, data: tuple[dict]) -> None:
        """Insert many rows."""
        command = """
            INSERT INTO player_detail (username, level, score, completed)
            VALUES (:username, :level, :score, :completed)
        """

        with self.cursor as cursor:
            cursor.executemany(command, data)
        self.connection.commit()

    def get_map_coordinates(self, username: str) -> tuple | None:
        """Get map coordinate of user."""
        with self.cursor as cursor:
            cursor.execute(
                """
                SELECT coord_x, coord_y
                FROM map
                WHERE username = ?
            """,
                (username,),
            )

            row = cursor.fetchone()
            if row:
                return row["coord_x"], row["coord_y"]
            return None

    def update_map_coordinates(self, username: str, coord_x: int, coord_y: int) -> None:
        """Update map coordinate of user."""
        # check if user exists in database
        with self.cursor as cursor:
            cursor.execute(
                """
                SELECT username
                FROM map
                WHERE username = ?
            """,
                (username,),
            )

            user = cursor.fetchone()

        if user is not None:
            command = """
                UPDATE map
                SET coord_x = ?, coord_y = ?
                WHERE username = ?
            """
        else:
            command = """
            INSERT INTO map(coord_x, coord_y, username)
            VALUES (?,?,?);
            """

        self.execute_command(command, (coord_x, coord_y, username))
