from api.base_client import APIClient

# Converts a ZIP code into latitude, longitude, city, and state metadata.
class Geocoder(APIClient):
    def lookup(self, zipcode):
        # Query the ZIP code API and extract the first matching location.
        data = self.get(f"https://api.zippopotam.us/us/{zipcode}")

        place = data["places"][0]
        return {
            "lat": float(place["latitude"]),
            "lon": float(place["longitude"]),
            "city": place["place name"],
            "state": place["state abbreviation"],
        }
