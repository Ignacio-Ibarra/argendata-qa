import logging
import sys
from datetime import datetime

import pytz

from utils.colors import Color


class LoggerFormatter(logging.Formatter):

    @staticmethod
    def __format__(color: callable):
        return Color.grey("[%(asctime)s] ") + \
            color("[%(levelname)s] ") + \
            Color.yellow("[%(name)s] ") + \
            "%(message)s "

    FORMATS = {
        logging.DEBUG: __format__(Color.green),
        logging.INFO: __format__(Color.blue),
        logging.WARNING: __format__(Color.red),
        logging.ERROR: __format__(Color.red_bright),
        logging.CRITICAL: __format__(Color.red_bright)
    }

    @staticmethod
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        tzinfo = pytz.timezone('Etc/GMT+3')
        return tzinfo.localize(dt)

    def formatTime(self, record, datefmt=None):
        dt = LoggerFormatter.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%H:%M:%S")
        return formatter.format(record)


# TODO: Hacer ésta clase singleton para manejar el logging level programáticamente
# TODO: Dar una instancia a un logger global para poder hacer prints desde funciones aisladas.
class LoggerFactory:
    @staticmethod
    def getLogger(name):
        logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(LoggerFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return logger


def inject_logger(name_or_cls):
    """Decorador para el reemplazo sintáctico de 'log = LoggerFactory.getLogger(...)' """
    if isinstance(name_or_cls, str):
        def wrapper(cls):
            class NewClass(cls):
                log = LoggerFactory.getLogger(name_or_cls)

            return NewClass

        return wrapper
    else:
        class NewClass(name_or_cls):
            log = LoggerFactory.getLogger(name_or_cls.__name__)

        return NewClass
