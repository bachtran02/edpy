import logging
import logging.config

from .client import EdClient
from .events import *
from .models import *

EDSPY_DEFAULT_LOGGER = {
    'version': 1,
    'formatters': { 
        'default': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': { 
        'default': { 
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': { 
        'edspy.transport': {
            'handlers': ['default'],
            'level': 'INFO',
        }
    }
}

def enable_logger(config: dict = EDSPY_DEFAULT_LOGGER):
    try:
        logging.config.dictConfig(config)
    except Exception:
        pass


def listener(*events: Event):
    def wrapper(func):
        setattr(func, '_ed_events', events)
        return func
    return wrapper