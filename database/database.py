import sqlite3
from config.settings import DATABASE

# Lightweight SQLite wrapper that centralizes query execution for the repository layer.
class Database:
    def __init__(self):
        # Open a thread-safe connection to the configured database file.
        self.connection = sqlite3.connect(DATABASE, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def execute(self, query, params=()):
        # Run a statement and commit the result for persistence.
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetchall(self, query, params=()):
        # Return all matching rows for a query.
        return self.execute(query, params).fetchall()

    def fetchone(self, query, params=()):
        # Return a single matching row for a query.
        return self.execute(query, params).fetchone()
