from api.base_client import APIClient

class Geocoder(APIClient):
    def lookup(self, zipcode):

        data = self.get(f"https://api.zippopotam.us/us/{zipcode}")

        place = data["places"][0]
        return {
            "lat": float(place["latitude"]),
            "lon": float(place["longitude"]),
            "city": place["place name"],
            "state": place["state abbreviation"],
        }