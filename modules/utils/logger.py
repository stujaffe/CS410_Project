import logging
import os


class CustomLogger(object):
    loggers = set()

    def __init__(
        self,
        logger_name: str = os.path.basename(__file__),
        log_level: str = "INFO",
        handlers: list = [],
    ) -> None:
        if type(handlers) != list:
            raise Exception(
                f"Excepting a list for attribute handlers. Received type {type(handlers)}."
            )
        self.logger_name = logger_name
        self.logger = logging.getLogger(name=logger_name)
        self.hanlders = handlers
        if logger_name not in self.loggers:
            self.loggers.add(logger_name)
            self.logger.level = getattr(logging, log_level)
            for i in range(len(handlers)):
                self.logger.addHandler(handlers[i])

    def get_logger(self) -> logging.Logger:
        return self.logger


class StreamLogging(logging.StreamHandler):
    def __init__(self, log_level: str = "INFO") -> None:
        logging.StreamHandler.__init__(self)
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        format_date = "%d-%b-%y %H:%M:%S"
        formatter = logging.Formatter(fmt=format, datefmt=format_date)
        self.setFormatter(formatter)
        self.level = getattr(logging, log_level)


if __name__ == "__main__":
    pass
