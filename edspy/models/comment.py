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
    
    id: int
    user_id: int
    course_id: int
    thread_id: int
    origin_id: t.Optional[int]
    parent_id: t.Optional[int]
    editor_id: t.Optional[int]
    number: int
    type: str  # only seen comment
    kind: str  # only seen normal
    content: str
    document: str  # rendered version of content
    flag_count: int
    vote_count: int
    is_endorsed: bool
    is_anonymous: bool
    is_private: bool
    is_resolved: bool
    created_at: str
    updated_at: t.Optional[str]
    deleted_at: t.Optional[str]
    anonymous_id: int
    vote: int
    comments: t.List['Comment']
    user: t.Optional[CourseUser]

    def __init__(self, data: dict) -> None:
        self._raw = data
        for slot in self.__slots__:
            setattr(self, slot, data.get(slot))

    def __repr__(self):
        return f'<Comment id={self.id}>'