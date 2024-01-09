import typing as t
from enum import Enum

from .comment import Comment
from .user import CourseUser

class ThreadType(Enum):
    """Thread types when posting to Ed."""
    
    POST          = 'post'
    QUESTION      = 'question'
    ANNOUNCEMENT  = 'announcement'

    @classmethod
    def from_str(cls, thread_type: str) -> 'ThreadType':
        for item in cls:
            if item.value == thread_type:
                return item
        raise ValueError(f'Invalid thread type: {thread_type}')
            

class Thread:
    """Thread object"""

    __slots__ = ('_raw', 'id', 'user_id', 'course_id', 'editor_id', 'accepted_id', 'duplicate_id',
        'number', 'type', 'title', 'content', 'document', 'category', 'subcategory',
        'subsubcategory', 'flag_count', 'star_count', 'view_count', 'unique_view_count',
        'vote_count', 'reply_count', 'unresolved_count', 'is_locked', 'is_pinned',
        'is_private', 'is_endorsed', 'is_answered', 'is_student_answered', 'is_staff_answered',
        'is_archived', 'is_anonymous', 'is_megathread', 'anonymous_comments', 'approved_status',
        'created_at', 'updated_at', 'deleted_at', 'pinned_at', 'anonymous_id', 'vote',
        'is_seen', 'is_starred', 'is_watched', 'glanced_at', 'new_reply_count', 'duplicate_title',
        'answers', 'comments', 'user')
    
    id: int  # global post number
    user_id: int  # user who created the post
    course_id: int
    editor_id: int
    accepted_id: t.Optional[int]
    duplicate_id: t.Optional[int]
    number: int  # post number relative to the course
    type: ThreadType
    title: str
    content: str
    document: str  # rendered version of content
    category: str
    subcategory: str
    subsubcategory: str
    flag_count: int
    star_count: int
    view_count: int
    unique_view_count: int
    vote_count: int
    reply_count: int
    unresolved_count: int
    is_locked: bool
    is_pinned: bool
    is_private: bool
    is_endorsed: bool
    is_answered: bool
    is_student_answered: bool
    is_staff_answered: bool
    is_archived: bool
    is_anonymous: bool
    is_megathread: bool
    anonymous_comments: bool
    approved_status: str
    created_at: str
    updated_at: str
    deleted_at: t.Optional[str]
    pinned_at: t.Optional[str]
    anonymous_id: int
    vote: int
    is_seen: bool
    is_starred: bool
    is_watched: bool
    glanced_at: str
    new_reply_count: int
    duplicate_title: t.Optional[str]
    answers: list[Comment]
    comments: list[Comment]
    user: t.Optional[CourseUser]
    

    def __init__(self, data: dict):    
        self._raw = data
        for slot in self.__slots__:
            if slot == 'type' and (thread_type := data.get(slot)):
                setattr(self, slot, ThreadType.from_str(thread_type))
                continue
            setattr(self, slot, data.get(slot))

    def __repr__(self):
        return f'<Thread title={self.title} id={self.id}>'