from database.database import Database
db=Database()

db.execute("""
CREATE TABLE IF NOT EXISTS weather(
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    zip_code TEXT,
    temperature REAL,
    humidity REAL,
    precipitation_probability REAL,
    wind_speed REAL,
    forecast TEXT
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS scores(
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    plant INTEGER,
    bee INTEGER,
    butterfly INTEGER,
    habitat INTEGER
)
""")