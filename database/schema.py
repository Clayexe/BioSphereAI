from database.database import Database

# Initialize the database connection once for schema creation.
db = Database()

# Store the latest weather snapshot for each ZIP code refresh.
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

# Store the calculated environmental score breakdown for reporting and history.
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
