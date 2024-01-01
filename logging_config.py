import logging
from logging.handlers import RotatingFileHandler


def configure_logging():
    # Set up logging to a file
    log_formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # File handler
    log_file = 'your_log_file.log'
    file_handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=5)
    file_handler.setFormatter(log_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # Add both handlers to the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def create_logger(name):
    return logging.getLogger(name)
