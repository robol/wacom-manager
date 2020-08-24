#
# Author: Leonardo Robol <leo@robol.it>
#

import logging, os

logger = logging.getLogger('it.robol.WacomManager')

logging_level = os.getenv('WACOM_DEBUG', 'WARNING')

if not logging_level in [ 'INFO', 'DEBUG', 'WARNING', 'ERROR']:
    raise RuntimeException('Invalid debug leve specified')
else:
    if logging_level == 'INFO':
        level = logging.INFO
    elif logging_level == 'DEBUG':
        level = logging.DEBUG
    elif logging_level == 'WARNING':
        level = logging.WARNING
    elif logging_level == 'ERROR':
        level = logging.ERROR

logging.basicConfig(
    level = level
)

def getLogger():
    return logger


