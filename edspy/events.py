from .models.comment import Comment
from .models.course import Course
from .models.thread import Thread

class Event:
    pass

class ThreadNewEvent(Event):
   """Event when new thread is created"""

   def __init__(self, thread: Thread, course: Course) -> None:
      self.thread = thread
      self.course = course

class ThreadUpdateEvent(Event):
   """Event when a thread is updated (thread object may not be completed)"""
   
   def __init__(self, thread: Thread) -> None:
      self.thread = thread

class CommentNewEvent(Event):
   """Event when a new comment is made on a thread"""

   def __init__(self, comment: Comment) -> None:
      self.comment = comment

class CourseCountEvent(Event):
   pass
