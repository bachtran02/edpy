class Thread:

    __slots__ = ('id', 'user_id', 'course_id', 'original_id', 'editor_id', 'accepted_id',
        'duplicate_id', 'number', 'type', 'title', 'content', 'document', 'category',
        'subcategory', 'subsubcategory', 'flag_count', 'star_count', 'view_count',
        'unique_view_count', 'vote_count', 'reply_count', 'unresolved_count', 'is_locked',
        'is_pinned', 'is_private', 'is_endorsed', 'is_answered', 'is_student_answered',
        'is_staff_answered', 'is_archived', 'is_anonymous', 'is_megathread', 'anonymous_comments',
        'approved_status', 'created_at', 'updated_at', 'deleted_at', 'pinned_at', 'anonymous_id', 'vote',
        'is_seen', 'is_starred', 'is_watched', 'glanced_at', 'new_reply_count', 'duplicate_title', 'user',
        '_raw')

    def __init__(self, data: dict) -> None:
        self._raw = data
        for slot in self.__slots__:
            setattr(self, slot, data.get(slot))

class Course:

    __slots__ = ('code', 'created_at', 'features', 'id', 'is_lab_regex_active', 
        'name', 'realm_id', 'session', 'settings', 'status', 'year', '_raw')
    
    def __init__(self, data: dict) -> None:
        self._raw = data
        for slot in self.__slots__:
            setattr(self, slot, data.get(slot))