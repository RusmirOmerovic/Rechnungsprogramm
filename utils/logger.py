import logging
import os

# Ordner für Logs anlegen, falls nicht vorhanden
os.makedirs("logs", exist_ok=True)

# Logging-Konfiguration
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S"
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
