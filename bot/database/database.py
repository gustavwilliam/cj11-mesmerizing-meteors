import sqlite3
from pathlib import Path

PATH = Path(__file__).parent  # Path of the database


class Database:
    """Class that handles interactions with the database."""

    def __init__(self) -> None:
        name = PATH.joinpath("score.db")
        self.__connection = sqlite3.connect(name)  # name must end with .db
        self.__cursor = self.__connection.cursor()

    def execute_command(self, command: str, data: tuple = ()) -> bool:
        """Execute the given command."""
        if self.__cursor.execute(command, data):
            self.__connection.commit()
            return True
        return False

    """
    @params:
        - name: Name of the table

    @returns: True if no problem occured. False otherwise
    """

    def add_table(self, name: str) -> bool:
        """Add new table in the database."""
        command = f"""CREATE TABLE IF NOT EXISTS {name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                score INTEGER NOT NULL,
                date DATE NOT NULL)
                """
        return self.execute_command(command)

    """
    @params:
        - table: Name of the table
        - values: dictionary containing the values of the record

    @returns: True if no problem occured. False otherwise
    """

    def add_record(self, table: str, values: dict) -> bool:
        """Add new record(or line) in the database.

        The `values` dictionary must have the following format:
        {
            "username": username,
            "score": score,
            "date": date
        }.
        """
        command = "INSERT INTO {} (username, score, date) VALUES (?, ?, ?)"
        command = command.format(table)
        data = tuple(values.values())

        return self.execute_command(command, data)

    """
    @returns: True if no problem occured. False otherwise
    """

    def disconnect(self) -> bool:
        """Close the database connection."""
        return not bool(self.__connection.close())
