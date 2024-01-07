from .client import EdClient
from .events import *
from .models.comment import Comment
from .models.course import Course
from .models.thread import Thread, ThreadType

def listener(*events: Event):
    def wrapper(func):
        setattr(func, '_ed_events', events)
        return func
    return wrapper