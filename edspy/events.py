from .models.comment import Comment
from .models.thread import Thread

class Event:
    pass

class ThreadNewEvent(Event):
   """Event when new thread is created"""

   def __init__(self, thread: Thread) -> None:
      self.thread = thread

class ThreadUpdateEvent(Event):
   """Event when a thread is updated (thread object may not be completed)"""
   
   def __init__(self, thread: Thread) -> None:
      self.thread = thread

class ThreadDeleteEvent(Event):
   """Event when a thread is deleted"""

   def __init__(self, thread: Thread) -> None:
      self.thread = thread

class CommentNewEvent(Event):
   """Event when a new comment is made on a thread"""

   def __init__(self, comment: Comment) -> None:
      self.comment = comment

class CommentUpdateEvent(Event):
   """Event when a comment is updated (comment object may be incomplete)"""

   def __init__(self, comment: Comment) -> None:
      self.comment = comment

class CommentDeleteEvent(Event):
   """Event when a comment is deleted"""
   
   def __init__(self, comment: Comment) -> None:
      self.comment = comment

class CourseCountEvent(Event):
   """Event when a user enters course page"""

   def __init__(self, course_id, count) -> None:
      self.course_id = course_id
      self.count = count