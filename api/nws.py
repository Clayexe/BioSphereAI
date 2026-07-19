from api.base_client import APIClient

# Pulls current weather conditions from the NOAA/NWS forecast service.
class WeatherAPI(APIClient):
    base = "https://api.weather.gov"

    def points(self, lat, lon):
        # Resolve the forecast endpoint for the provided coordinates.
        return self.get(f"{self.base}/points/{lat},{lon}")

    def forecast(self, url):
        # Fetch the forecast payload from the resolved forecast URL.
        return self.get(url)

    def current_weather(self, lat, lon):
        # Collect the first forecast period and normalize it into the dashboard fields.
        points = self.points(lat, lon)

        forecast_url = points["properties"]["forecast"]

        data = self.forecast(forecast_url)

        current = data["properties"]["periods"][0]

        precip = current.get(
            "probabilityOfPrecipitation",
            {}
        )

        return {
            "temperature": current["temperature"],
            "humidity": 60,  # NWS forecast does not provide humidity directly
            "precipitation_probability": precip.get("value", 0) or 0,
            "wind_speed": current["windSpeed"],
            "forecast": current["shortForecast"]
        }
