import requests
from config.settings import USER_AGENT

# Shared HTTP wrapper for external API calls used across the BioSphereAI project.
class APIClient:
    def __init__(self):
        # Create one reusable session so requests can share headers and connection settings.
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})

    def get(self, url, params=None):
        # Perform a GET request and return JSON data when the API response is successful.
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
