"""
TODO
"""
import sqlite3
import time

class SQLHandler:

    def __init__(self, db="debug.db"):
        self._db = db
        self._con = sqlite3.connect(db)
        self._cur = self._con.cursor()
        self._setup_db()

    def _setup_db(self) -> None:
        self._cur.execute("""CREATE TABLE IF NOT EXISTS 
                            variables(
                            name TEXT PRIMARY KEY,
                            value TEXT,
                            timestamp REAL
                          )""")
        self._cur.execute("""CREATE TABLE IF NOT EXISTS
                            songs(
                            name TEXT PRIMARY KEY,
                            link TEXT,
                            timestamp REAL
                          )""")
        
    def add_to_table(self, table: str, name: str, value: any) -> None:
        """
        Add an element to the table of the database.
        
        :param table: The name of the table to add to.
        :type table: str
        :param name: The name of the variable to be added.
        :type name: str
        :param value: The value of the variable to be added.
        :type value: any
        """
        self._cur.execute(f"""INSERT INTO {table} (name, value, timestamp)
                                VALUES (?, ?, ?)
                                ON CONFLICT DO UPDATE SET
                                value = excluded.value,
                                timestamp = excluded.timestamp
                                """, (str(name), str(value), time.time()))
        self._con.commit()
    
    def get_from_table(self, table: str, name: str) -> list[str]:
        """
        Get a variables value from a table.
        
        :param table: The name of the table to get from.
        :type table: str
        :param name: The name of the variable to read.
        :type name: str
        :return: The value of the variable that was gotten.
        :rtype: list[str]
        """
        self._cur.execute(f"""SELECT VALUE FROM {table} WHERE name = '{name}'""")
        row = self._cur.fetchone()

        return row