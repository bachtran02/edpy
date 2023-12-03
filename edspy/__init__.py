import logging
import logging.config
from dotenv import load_dotenv

from .client import EdClient
from .events import *
from .models import *

load_dotenv()

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
        'edspy.client': {
            'handlers': ['default'],
            'level': 'INFO',
        }
    }
}

def enable_logger(config: dict = EDSPY_DEFAULT_LOGGER):
    
    try:
        assert config is not None
        logging.config.dictConfig(config)
    except Exception as e:
        pass
    else:
        return
    
    logging.config.dictConfig(EDSPY_DEFAULT_LOGGER)


def listener(*events: Event):
    def wrapper(func):
        setattr(func, '_ed_events', events)
        return func
    return wrapper