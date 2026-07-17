from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE = os.getenv(
    "DATABASE", BASE_DIR / "data" / "biosphere.db")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

USER_AGENT = os.getenv("USER_AGENT", "BioSphereAI/0.1 (roamwithclay@gmail.com)")

REFRESH_MINUTES = int(os.getenv("REFRESH_MINUTES", 30))
