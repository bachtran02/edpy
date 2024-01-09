import typing as t

from ..thread import Thread
from ..user import CourseUser

class GetThreadType:

    def __init__(self, thread: Thread, users: t.List[CourseUser]) -> None:
        self.thread: Thread = thread
        self.users: t.List[CourseUser] = users
