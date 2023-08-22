import logging
import sys


def set_up_logging():
    enable_stream_logging = True
    enable_file_logging = True

    # https://towardsdatascience.com/python-logging-saving-logs-to-a-file-sending-logs-to-an-api-75ec5964943f
    logger = logging.getLogger('IND-RegisterExplorer')
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
        file_handler = logging.FileHandler(filename='IND-RegisterExplorer.log')  # handler for file writing
        file_handler.setFormatter(log_file_formatter)  # apply the format to the file handler
        file_handler.setLevel(level=logging.DEBUG)

        logger.addHandler(file_handler)  # add the file handler to the logging object

    return logger


def main():
    set_up_logging()


if __name__ == '__main__':
    main()
