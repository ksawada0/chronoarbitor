from functools import cache
import logging
import os
import json

# TIME_FORMAT = "[%Y-%m-%d %H:%M:%S.%f]"
TIME_FORMAT = "[%Y-%m-%d %H:%M:%S]"
LOG_FORMAT = "[%(name)s] %(message)s"

from rich.logging import RichHandler

logging.basicConfig(
    level=os.environ.get("CHRONO_LOGLEVEL", "INFO"),
    format=f"{LOG_FORMAT}",
    datefmt=f"{TIME_FORMAT}",
    handlers=[RichHandler()],
)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'time': self.formatTime(record, self.datefmt),
            'name': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'pathname': record.pathname,
            'lineno': record.lineno,
            'funcName': record.funcName
        }
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

@cache
def get_logger(name, json=True) -> logging.Logger:
    if json:
        return get_json_logger(name)
    else:
        return get_normal_logger(name)


@cache
def get_normal_logger(name) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(name)

    logging.basicConfig(
        level=os.environ.get("CHRONO_LOGLEVEL", "INFO"),
        format=f"{LOG_FORMAT}",
        datefmt=f"{TIME_FORMAT}",
        handlers=[RichHandler()],
    )

    return logger


@cache
def get_json_logger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Set log level from environment variable or default to INFO
    log_level = os.environ.get("CHRONO_LOGLEVEL", "INFO").upper()
    logger.setLevel(log_level)
    
    # Create a stream handler
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    
    # Use the custom JSON formatter
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(handler)
    
    return logger

