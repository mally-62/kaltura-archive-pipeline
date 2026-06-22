# logger.py
import logging
from config import LOG_PATH

def setup_logging():
    # Configures logging for the entire project
    # Call once at the start of main.py before anything else runs

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Format applied to every log message
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Terminal - INFO and above only
    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(logging.INFO)
    terminal_handler.setFormatter(formatter)

    # Log file - everything including DEBUG
    file_handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Connect both handlers to the root logger
    root_logger.addHandler(terminal_handler)
    root_logger.addHandler(file_handler)

    logging.info("Logging initialized - writing to %s", LOG_PATH)