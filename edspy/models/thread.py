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

    __slots__ = ('_raw', 'id', 'user_id', 'course_id', 'original_id', 'editor_id', 'accepted_id',
        'duplicate_id', 'number', 'type', 'title', 'content', 'document', 'category', 'subcategory',
        'subsubcategory', 'flag_count', 'star_count', 'view_count', 'unique_view_count',
        'vote_count', 'reply_count', 'unresolved_count', 'is_locked', 'is_pinned',
        'is_private', 'is_endorsed', 'is_answered', 'is_student_answered', 'is_staff_answered',
        'is_archived', 'is_anonymous', 'is_megathread', 'anonymous_comments', 'approved_status',
        'created_at', 'updated_at', 'deleted_at', 'pinned_at', 'anonymous_id', 'vote',
        'is_seen', 'is_starred', 'is_watched', 'glanced_at', 'new_reply_count', 'duplicate_title',
        'answers', 'comments', 'user')
    
    def __init__(self, data: dict, id: int = None, user_id: int = None, course_id: int = None, original_id: int = None, 
            editor_id: int = None, accepted_id: t.Optional[int] = None, duplicate_id: t.Optional[int] = None,
            number: int = None, type: ThreadType = None, title: str = None, content: str = None,
            document: str = None, category: str = None, subcategory: str = None, subsubcategory: str = None,
            flag_count: int = None, star_count: int = None, view_count: int = None,
            unique_view_count: int = None, vote_count: int = None, reply_count: int = None,
            unresolved_count: int = None, is_locked: bool = None, is_pinned: bool = None,
            is_private: bool = None, is_endorsed: bool = None, is_answered: bool = None,
            is_student_answered: bool = None, is_staff_answered: bool = None, is_archived: bool = None,
            is_anonymous: bool = None, is_megathread: bool = None, anonymous_comments: bool = None,
            approved_status: str = None, created_at: str = None, updated_at: str = None,
            deleted_at: t.Optional[str] = None, pinned_at: t.Optional[str] = None,
            anonymous_id: int = None, vote: int = None, is_seen: bool = None, is_starred: bool = None,
            is_watched: bool = None, glanced_at: str = None, new_reply_count: int = None,
            duplicate_title: t.Optional[str] = None, answers: list[Comment] = None,
            comments: list[Comment] = None, user: t.Optional[CourseUser] = None):
        
        self._raw = data
        self.id: int = id
        self.user_id: int = user_id
        self.course_id: int = course_id
        self.original_id: int = original_id
        self.editor_id: int = editor_id
        self.accepted_id: t.Optional[int] = accepted_id
        self.duplicate_id: t.Optional[int] = duplicate_id
        self.number: int = number
        self.type: ThreadType = ThreadType.from_str(type) if type else None
        self.title: str = title
        self.content: str = content
        self.document: str = document
        self.category: str = category
        self.subcategory: str = subcategory
        self.subsubcategory: str = subsubcategory
        self.flag_count: int = flag_count
        self.star_count: int = star_count
        self.view_count: int = view_count
        self.unique_view_count: int = unique_view_count
        self.vote_count: int = vote_count
        self.reply_count: int = reply_count
        self.unresolved_count: int = unresolved_count
        self.is_locked: bool = is_locked
        self.is_pinned: bool = is_pinned
        self.is_private: bool = is_private
        self.is_endorsed: bool = is_endorsed
        self.is_answered: bool = is_answered
        self.is_student_answered: bool = is_student_answered
        self.is_staff_answered: bool = is_staff_answered
        self.is_archived: bool = is_archived
        self.is_anonymous: bool = is_anonymous
        self.is_megathread: bool = is_megathread
        self.anonymous_comments: bool = anonymous_comments
        self.approved_status: str = approved_status
        self.created_at: str = created_at
        self.updated_at: str = updated_at
        self.deleted_at: t.Optional[str] = deleted_at
        self.pinned_at: t.Optional[str] = pinned_at
        self.anonymous_id: int = anonymous_id
        self.vote: int = vote
        self.is_seen: bool = is_seen
        self.is_starred: bool = is_starred
        self.is_watched: bool = is_watched
        self.glanced_at: str = glanced_at
        self.new_reply_count: int = new_reply_count
        self.duplicate_title: t.Optional[str] = duplicate_title
        self.answers: list[Comment] = answers
        self.comments: list[Comment] = comments
        self.user: t.Optional[CourseUser] = user

    def __repr__(self):
        return f'<Thread id={self.id}>'