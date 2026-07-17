from api.geocoder import Geocoder
from api.nws import WeatherAPI

class WeatherService:
    def __init__(self):
        self.geocoder = Geocoder()
        self.weather_api = WeatherAPI()

    def get_by_zip(self,zipcode):
        location = self.geocoder.lookup(zipcode)
        weather=self.weather_api.current_weather(location['lat'],location['lon'])
        weather.update(location)
        weather['zip_code']=zipcode

        return weather
