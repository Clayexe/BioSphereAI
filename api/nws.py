import requests

from api.base_client import APIClient

# Pulls current weather conditions from the NOAA/NWS forecast service.
class WeatherAPI(APIClient):
    base = "https://api.weather.gov"
    open_meteo_base = "https://api.open-meteo.com/v1/forecast"

    def points(self, lat, lon):
        # Resolve the forecast endpoint for the provided coordinates.
        return self.get(f"{self.base}/points/{lat},{lon}")

    def forecast(self, url):
        # Fetch the forecast payload from the resolved forecast URL.
        return self.get(url)

    def current_weather(self, lat, lon):
        # Try NOAA/NWS first and fall back to Open-Meteo when the coordinates are unavailable.
        try:
            points = self.points(lat, lon)
            forecast_url = points["properties"]["forecast"]
            data = self.forecast(forecast_url)

            current = data["properties"]["periods"][0]
            precip = current.get("probabilityOfPrecipitation", {})

            return {
                "temperature": current["temperature"],
                "humidity": 60,
                "precipitation_probability": precip.get("value", 0) or 0,
                "wind_speed": current["windSpeed"],
                "forecast": current["shortForecast"],
            }
        except (requests.HTTPError, requests.RequestException, KeyError, ValueError):
            return self.current_weather_open_meteo(lat, lon)

    def current_weather_open_meteo(self, lat, lon):
        # Use Open-Meteo as a fallback for coordinates not covered by NOAA/NWS.
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation_probability,wind_speed_10m,weather_code",
            "timezone": "auto",
        }
        data = self.get(self.open_meteo_base, params=params)

        current = data.get("current", {})
        weather_code = current.get("weather_code", 0)
        forecast = self._forecast_label(weather_code)

        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m", 0),
            "precipitation_probability": current.get("precipitation_probability", 0),
            "wind_speed": f"{current.get('wind_speed_10m', 0)} km/h",
            "forecast": forecast,
        }

    def _forecast_label(self, weather_code):
        labels = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            95: "Thunderstorm",
        }
        return labels.get(weather_code, "Weather conditions")
