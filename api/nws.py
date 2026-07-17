from api.base_client import APIClient

class WeatherAPI(APIClient):
    base="https://api.weather.gov"

    def points(self,lat,lon):
        return self.get(f"{self.base}/points/{lat},{lon}")
    
    def forecast(self, url):

        return self.get(url)

    def current_weather(self, lat, lon):

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