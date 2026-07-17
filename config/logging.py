import logging

loggging.basicConfig(
    filename="logs/biosphere.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("BiosphereAI")