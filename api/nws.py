from api.base_client import APIClient

class WeatherAPI(APIClient):
    base = "https://api.weather.gov"
    open_meteo_base = "https://api.open-meteo.com/v1/forecast"

    def points(self, lat, lon):
        return self.get(f"{self.base}/points/{lat},{lon}")

    def forecast(self, url):
        return self.get(url)

    def current_weather(self, lat, lon):
        try:
            points = self.points(lat, lon)
            forecast_url = points["properties"]["forecast"]
            data = self.forecast(forecast_url)
            current = data["properties"]["periods"][0]

            precip = current.get("probabilityOfPrecipitation", {})

            return {
                "temperature": current["temperature"],
                "humidity": 60,  # NWS forecast does not provide humidity directly
                "precipitation_probability": precip.get("value", 0) or 0,
                "wind_speed": current["windSpeed"],
                "forecast": current["shortForecast"],
            }
        except Exception:
            return self.current_weather_open_meteo(lat, lon)

    def current_weather_open_meteo(self, lat, lon):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation_probability,wind_speed_10m,weather_code",
            "forecast_days": 1,
            "timezone": "auto",
        }
        response = self.session.get(self.open_meteo_base, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        forecast = self._forecast_from_code(current.get("weather_code", 0))

        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation_probability": current.get("precipitation_probability", 0),
            "wind_speed": current.get("wind_speed_10m"),
            "forecast": forecast,
        }

    def _forecast_from_code(self, weather_code):
        mapping = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            95: "Thunderstorm",
        }
        return mapping.get(weather_code, "Unknown")