import logging
import os
from rich.console import Console

console = Console()

#Logging
LOG_FILE = "ai-pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        # logging.StreamHandler()terminal
    ]
)

logger = logging.getLogger("ai-pipeline")

def get_logger(name):
    return logging.getLogger(f"ai-pipeline.{name}")
