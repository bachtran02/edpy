class Course:
    """
    Course object
    """

    __slots__ = ('_raw', 'code', 'created_at', 'features', 'id', 'is_lab_regex_active', 
        'name', 'realm_id', 'session', 'settings', 'status', 'year')
    
    id: int
    realm_id: int
    code: str
    name: str
    year: str
    session: str
    status: str  # archived or active
    features: dict
    settings: dict
    created_at: str
    is_lab_regex_active: bool
    
    def __init__(self, data: dict) -> None:
        self._raw = data
        for slot in self.__slots__:
            setattr(self, slot, data.get(slot))

    def __repr__(self):
        return f'<Course code={self.code} id={self.id}>'