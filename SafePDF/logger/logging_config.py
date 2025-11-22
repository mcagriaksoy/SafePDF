"""Central logging setup for SafePDF.

Place this file inside the `SafePDF/` package and call
`from SafePDF.logging_config import setup_logging` early in the
application startup (for example in `safe_pdf_app.py`) so the
root logger and file handlers are configured before other modules
obtain loggers.

Usage:
    from SafePDF.logging_config import setup_logging, get_logger
    setup_logging()  # call once at startup
    logger = get_logger(__name__)
    logger.info("Ready")
"""
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os

DEFAULT_LOG_DIR_NAME = ".safepdf"
DEFAULT_LOG_FILE = "safepdf.log"

_configured = False
_log_file_path = None

def setup_logging(log_dir: str | None = None, max_bytes: int = 5 * 1024 * 1024, backup_count: int = 3):
    """Configure root logger with a rotating file handler.

    Call this once early in application startup (before other modules
    obtain module loggers).

    Returns the `Path` to the log file.
    """
    global _configured, _log_file_path

    if _configured:
        return _log_file_path

    # Determine log directory
    if log_dir:
        log_dir_path = Path(log_dir).expanduser()
    else:
        log_dir_path = Path.home() / DEFAULT_LOG_DIR_NAME

    try:
        log_dir_path.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Fall back to current working directory
        log_dir_path = Path.cwd()

    _log_file_path = log_dir_path / DEFAULT_LOG_FILE

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    handler = RotatingFileHandler(str(_log_file_path), maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    # Avoid adding multiple handlers when setup_logging is called more than once
    if not any(isinstance(h, RotatingFileHandler) and getattr(h, 'baseFilename', None) == str(_log_file_path) for h in root.handlers):
        root.addHandler(handler)

    # Optional: also emit warnings to console in development
    # if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
    #     console = logging.StreamHandler()
    #     console.setFormatter(formatter)
    #     console.setLevel(logging.INFO)
    #     root.addHandler(console)

    _configured = True
    return _log_file_path


def get_logger(name: str):
    """Return a logger for the given name. Call `setup_logging()` first.

    If `setup_logging()` was not called, this still returns a logger
    but logs will follow the default logging behaviour.
    """
    return logging.getLogger(name)


def get_log_file_path():
    return _log_file_path
