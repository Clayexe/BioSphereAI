from apscheduler.schedulers.background import BackgroundScheduler

from services.weather_service import WeatherService
from database.repository import save_weather
from database.repository import save_scores

from analytics.plant import calculate as plant_score
from analytics.pollinator import calculate as bee_score
from analytics.butterfly import calculate as butterfly_score
from analytics.habitat import calculate as habitat_score

scheduler = BackgroundScheduler()

service = WeatherService()

def update():

    weather = service.get_by_zip("13760")

    save_weather(weather)

    plant = plant_score(weather)
    bee = bee_score(weather)
    butterfly = butterfly_score(weather)

    habitat = habitat_score(
        plant,
        bee,
        butterfly
    )

    save_scores(
        plant,
        bee,
        butterfly,
        habitat
    )

scheduler.add_job(
    update,
    "interval",
    minutes=30
)

scheduler.start()