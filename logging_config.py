import logging
import sys
from pathlib import Path


def set_up_logging() -> logging.Logger:
    """
    Set up logging for the IND-RegisterExplorer application.

    This function configures logging for the IND-RegisterExplorer application.
    It sets up both console and file logging, with customizable formatting
    options for each. Log files are saved in the grandparent folder of the script (application main folder).

    :return: Logger instance configured for the application.
    :rtype: logging.Logger
    """
    enable_stream_logging = True
    enable_file_logging = True

    # https://towardsdatascience.com/python-logging-saving-logs-to-a-file-sending-logs-to-an-api-75ec5964943f
    logger = logging.getLogger('IND-RegisterExplorer')

    # If handlers are already configured, return the existing logger
    if logger.handlers:
        return logger

    logger.setLevel(level=logging.DEBUG)  # set the default level

    basic_formatting = f"%(message)s"
    basic_date_formatting = None
    verbose_formatting = f"%(levelname)s %(asctime)s (%(relativeCreated)d) \t " \
                         f"%(pathname)s @%(funcName)s L%(lineno)s - %(message)s"
    verbose_date_formatting = "%Y-%m-%d %H:%M:%S"

    if enable_stream_logging:
        # Format for the console out stream
        log_stream_formatter = logging.Formatter(fmt=basic_formatting, datefmt=basic_date_formatting)
        console_handler = logging.StreamHandler(stream=sys.stdout)  # handler for console out
        console_handler.setFormatter(log_stream_formatter)  # apply the format to the console handler
        console_handler.setLevel(level=logging.DEBUG)

        logger.addHandler(console_handler)  # add the console handler to the logging object

    if enable_file_logging:
        # Format for the file writing stream
        log_file_formatter = logging.Formatter(fmt=verbose_formatting, datefmt=verbose_date_formatting)

        script_dir = Path(__file__).resolve().parent
        log_file = script_dir / "IND-RegisterExplorer.log"
        file_handler = logging.FileHandler(filename=log_file)  # handler for file writing

        file_handler.setFormatter(log_file_formatter)  # apply the format to the file handler
        file_handler.setLevel(level=logging.DEBUG)

        logger.addHandler(file_handler)  # add the file handler to the logging object

    return logger


def main():
    set_up_logging()


if __name__ == '__main__':
    main()
