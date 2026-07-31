from database.database import Database

db = Database()

def save_weather(weather):

    db.execute("""
    INSERT INTO weather(
        zip_code,
        temperature,
        humidity,
        precipitation_probability,
        wind_speed,
        forecast
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        weather["zip_code"],
        weather["temperature"],
        weather["humidity"],
        weather["precipitation_probability"],
        weather["wind_speed"],
        weather["forecast"]
    ))

def save_scores(plant, bee, butterfly, habitat):

    db.execute("""
    INSERT INTO scores(
        plant,
        bee,
        butterfly,
        habitat
    )
    VALUES (?, ?, ?, ?)
    """, (
        plant,
        bee,
        butterfly,
        habitat
    ))