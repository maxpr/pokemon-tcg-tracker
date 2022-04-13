import logging
import os

import coloredlogs

FIELD_STYLES = dict(
    asctime=dict(color="green"),
    hostname=dict(color="magenta"),
    levelname=dict(color="black", bold=True),
    name=dict(color="blue"),
    message=dict(color="white"),
)


def get_logger(name: str, level: str = logging.INFO) -> logging.Logger:
    """
    Returns the logger we use for output
    :param name: the name of your logger, usually __name__
    :param level: the level to which your logger logs
    :return: the logger
    """

    log_format = "[%(asctime)s] [%(name)-51s] [%(levelname)s] %(message)s"
    logger = logging.getLogger(name)

    # To override the default severity of logging
    logger.setLevel(level)
    logger.propagate = False

    # Use FileHandler() to log to a file
    path = f"logs/logger_worker.log"
    os.makedirs("/".join(path.split("/")[:-1]), exist_ok=True)
    file_handler = logging.FileHandler(path)
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Don't forget to add the console handler
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    coloredlogs.install(logger=logger, level=level, field_styles=FIELD_STYLES, fmt=log_format)
    return logger


LOGGER = get_logger(__name__)
