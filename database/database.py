import sqlite3
from config.settings import DATABASE

class Database:
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def execute(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor
    
    def fetchall(self,query, params=()):
        return self.execute(query, params).fetchall()
    
    def fetchone(self, query, params=()):
        return self.execute(query, params).fetchone()