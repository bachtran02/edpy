import logging
import logging.config

from .client import EdClient
from .events import *
from .models import *

def listener(*events: Event):
    def wrapper(func):
        setattr(func, '_ed_events', events)
        return func
    return wrapper