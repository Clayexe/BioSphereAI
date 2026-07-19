from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from the local .env file when available.
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# Local database path used by the SQLite repository layer.
DATABASE = os.getenv(
    "DATABASE", BASE_DIR / "data" / "biosphere.db")

# Logging level for the project-wide logger configuration.
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Default HTTP user-agent used when calling external weather APIs.
USER_AGENT = os.getenv("USER_AGENT", "BioSphereAI/0.1 (roamwithclay@gmail.com)")

# Default refresh interval for scheduled updates.
REFRESH_MINUTES = int(os.getenv("REFRESH_MINUTES", 30))
