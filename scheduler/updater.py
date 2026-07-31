try:
    from apscheduler.schedulers.background import BackgroundScheduler
except ImportError:
    import threading

    class BackgroundScheduler:
        def __init__(self):
            self._timer = None
            self._job = None
            self._interval = None

        def add_job(self, func, trigger, minutes=0):
            self._job = func
            self._interval = minutes * 60

        def _run_job(self):
            if self._job is None:
                return
            self._job()
            self._timer = threading.Timer(self._interval, self._run_job)
            self._timer.daemon = True
            self._timer.start()

        def start(self):
            if self._job is None or self._interval is None:
                return
            self._timer = threading.Timer(self._interval, self._run_job)
            self._timer.daemon = True
            self._timer.start()

from services.weather_service import WeatherService
from database.repository import save_weather
from database.repository import save_scores

from analytics.plant import calculate as plant_score
from analytics.pollinator import calculate as bee_score
from analytics.butterfly import calculate as butterfly_score
from analytics.habitat import calculate as habitat_score

# Background scheduler that refreshes the stored weather and score history.
scheduler = BackgroundScheduler()

# Shared service instance used to keep the refresh process consistent.
service = WeatherService()

# Pull the latest weather, store it, and then compute and save the ecosystem scores.
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