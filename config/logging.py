import logging

# Configure the application logger so messages are written to a persistent log file.
logging.basicConfig(
    filename="logs/biosphere.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("BiosphereAI")
