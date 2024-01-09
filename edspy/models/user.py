class CourseUser:
    
    __slots__ = ('_raw', 'avatar', 'course_role', 'id', 'name', 'role', 'tutorials')  
        
    avatar: str
    course_role: str
    id: int
    name: str
    role: str
    tutorials: dict[int, str]

    def __init__(self, data):
        self._raw = data
        for slot in self.__slots__:
            setattr(self, slot, data.get(slot))

    def __repr__(self):
        return f'<CourseUser name={self.name} id={self.id}>'