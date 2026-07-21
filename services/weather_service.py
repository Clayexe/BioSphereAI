from geopy.geocoders import Nominatim

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

    def get_by_coords(self, lat, lon):
        # Fetch weather directly from coordinates and use reverse geocoding for the location label.
        weather = self.weather_api.current_weather(lat, lon)
        location = self._reverse_geocode(lat, lon)
        weather.update({
            "lat": float(lat),
            "lon": float(lon),
            "city": location.get("city") or location.get("town") or location.get("village") or "Selected location",
            "state": location.get("state") or location.get("state_code") or "Custom coordinates",
        })
        weather['zip_code'] = None

        return weather

    def _reverse_geocode(self, lat, lon):
        try:
            geocoder = Nominatim(user_agent="biosphereai")
            location = geocoder.reverse((lat, lon), exactly_one=True)
            if not location:
                return {}

            address = location.raw.get("address", {})
            return {
                "city": address.get("city") or address.get("town") or address.get("village") or address.get("suburb"),
                "state": address.get("state"),
                "state_code": address.get("state_code"),
            }
        except Exception:
            return {}
