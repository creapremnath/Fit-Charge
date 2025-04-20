import os
import logging
from logging.handlers import RotatingFileHandler
from config import settings

def validate_log_dir(logdir: str) -> None:
    """Ensure log directory exists."""
    os.makedirs(logdir, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    """Set up and return the application logger with rotating file support."""

    _logdir = str(settings.logpath)
    validate_log_dir(_logdir)

    log_file = os.path.join(_logdir, settings.logfile)

    # Use the passed name argument for logger
    logger = logging.getLogger(name)  # <-- Use the module name here

    # Prevent duplicate handlers in reloads (FastAPI, etc.)
    if logger.hasHandlers():
        return logger

    # Set log level using your settings.mode
    log_level = getattr(logging, settings.mode.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Formatter
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # Rotating File Handler
    file_handler = RotatingFileHandler(
        filename=log_file,
        mode='a',
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=3,             # Keep last 3 rotated logs
        encoding='utf-8',
        delay=False
    )
    file_handler.setLevel(log_level)  # apply your mode here
    file_handler.setFormatter(log_format)

    # Stream (Console) Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)  # same mode here too
    stream_handler.setFormatter(log_format)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


# No need to change this part; this will be used for module-specific logging
