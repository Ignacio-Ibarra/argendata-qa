from logging import Logger

from src import LoggerFactory
from test import *
import src
from unittest import TextTestRunner


def main(log: Logger):
    log.info('Corriendo tests unitarios...')
    suite = get_suite()
    TextTestRunner().run(suite)
    log.info('Ejecutando programa principal...')
    src.main(log)


if __name__ == '__main__':
    log = LoggerFactory.getLogger('main')
    try:
        main(log)
    except KeyboardInterrupt:
        log.info('Process interrupted by user. Finishing cleanly.')
        exit(0)
    except Exception as e:
        log.exception('\033[0;91mProcess interrupted by an Exception. Here are all the details:')
        print('\033[0m')
        exit(1)
