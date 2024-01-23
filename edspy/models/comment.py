import typing as t

from .user import CourseUser

class Comment:
    """
    Comment object
    """
    
    __slots__ = ( '_raw', 'id', 'user_id', 'course_id', 'thread_id', 'original_id',
        'parent_id', 'editor_id', 'number', 'type', 'kind', 'content', 'document', 'flag_count',
        'vote_count', 'is_endorsed', 'is_anonymous', 'is_private', 'is_resolved', 'created_at',
        'updated_at', 'deleted_at', 'anonymous_id', 'vote', 'comments', 'user')

    def __init__(self, data: dict, id: int = None, user_id: int = None, course_id: int = None, thread_id: int = None,
            original_id: t.Optional[int] = None, parent_id: t.Optional[int] = None,
            editor_id: t.Optional[int] = None, number: int = None, type: str = None, kind: str = None,
            content: str = None, document: str = None, flag_count: int = None, vote_count: int = None,
            is_endorsed: bool = None, is_anonymous: bool = None, is_private: bool = None,
            is_resolved: bool = None, created_at: str = None, updated_at: t.Optional[str] = None,
            deleted_at: t.Optional[str] = None, anonymous_id: int = None, vote: int = None,
            comments: t.List['Comment'] = None, user: t.Optional[CourseUser] = None):
        
        self._raw = data
        self.id: int = id
        self.user_id: int = user_id
        self.course_id: int = course_id
        self.thread_id: int = thread_id
        self.original_id: t.Optional[int] = original_id
        self.parent_id: t.Optional[int] = parent_id
        self.editor_id: t.Optional[int] = editor_id
        self.number: int = number
        self.type: str = type
        self.kind: str = kind
        self.content: str = content
        self.document: str = document
        self.flag_count: int = flag_count
        self.vote_count: int = vote_count
        self.is_endorsed: bool = is_endorsed
        self.is_anonymous: bool = is_anonymous
        self.is_private: bool = is_private
        self.is_resolved: bool = is_resolved
        self.created_at: str = created_at
        self.updated_at: t.Optional[str] = updated_at
        self.deleted_at: t.Optional[str] = deleted_at
        self.anonymous_id: int = anonymous_id
        self.vote: int = vote
        self.comments: t.List['Comment'] = comments
        self.user: t.Optional[CourseUser] = user

    def __repr__(self):
        return f'<Comment id={self.id}>'