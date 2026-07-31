from api.geocoder import Geocoder
from api.nws import WeatherAPI

# Orchestrates location lookup and live weather retrieval for the UI and scheduler.
class WeatherService:
    def __init__(self):
        # Compose the geocoder and weather API so the service can fetch both location and forecast data.
        self.geocoder = Geocoder()
        self.weather_api = WeatherAPI()

    def get_by_zip(self, zipcode):
        # Convert the ZIP code to coordinates, fetch weather, then merge the two payloads.
        location = self.geocoder.lookup(zipcode)
        weather = self.weather_api.current_weather(location['lat'], location['lon'])
        weather.update(location)
        weather['zip_code'] = zipcode

        return weather

    def _reverse_geocode(self, lat, lon):
        # Provide a fallback location payload for coordinate-based lookups.
        return {
            "lat": lat,
            "lon": lon,
            "city": "",
            "state": "",
        }

    def get_by_coords(self, lat, lon):
        # Fetch weather for coordinates and merge a basic location payload.
        weather = self.weather_api.current_weather(lat, lon)
        location = self._reverse_geocode(lat, lon)
        weather.update({"lat": lat, "lon": lon})
        weather.update(location)
        return weather