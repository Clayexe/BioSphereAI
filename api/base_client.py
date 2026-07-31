import requests
from config.settings import USER_AGENT

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})

    def get(self, url, params=None):
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()