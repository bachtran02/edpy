import sys
import logging
from dotenv import load_dotenv

from .client import EdClient
from .events import *
from .models import *

load_dotenv()

# config logger
log = logging.getLogger('edspy')

fmt = logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S')

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(fmt)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


def listener(*events: Event):
    def wrapper(func):
        setattr(func, '_ed_events', events)
        return func
    return wrapper