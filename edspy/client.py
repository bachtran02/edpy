import asyncio

import typing as t
from collections import defaultdict
from inspect import getmembers, ismethod

from .models.thread import Thread, ThreadType
from .models.user import CourseUser
from .models.endpoints.threads import GetThreadType

from .transport import Transport

def _ensure_login(func):
    """
    Decorator to ensure valid ed API key before calling the methods.
    """

    async def login_wrapper(self, *args, **kwargs):
        if not self.logged_in:
            await self._login()
        return await func(self, *args, **kwargs)

    return login_wrapper

class EdClient():

    def __init__(self, ed_token: str = None) -> None:

        self._event_hooks = defaultdict(list)
        self._transport = Transport(self, ed_token)
        
        self.logged_in = False
        self.user, self.user_courses = None, None

    async def _login(self):
        
        res = await self._transport._request('GET', '/api/user')
        self.user = res.get('user')
        self.user_courses = res.get('courses')
        self.logged_in = True

    @_ensure_login
    async def subscribe(self, course_ids: list = None):

        course_ids = course_ids or [course['course']['id'] for course in self.user_courses]

        for course_id in course_ids:
            assert isinstance(course_id, int)
            await self._transport._send({'type': 'course.subscribe', 'oid': course_id})

        await self._transport._connect()
        
    @_ensure_login
    async def get_thread(self, thread_id) -> GetThreadType:

        res = await self._transport._request('GET', f'/api/threads/{thread_id}')
        thread = Thread(res.get('thread'))
        users = [CourseUser(user) for user in res.get('users')]
        return GetThreadType(thread=thread, users=users)


    def add_event_hooks(self, cls):
        
        methods = getmembers(cls, predicate=lambda meth: hasattr(meth, '__name__')
            and not meth.__name__.startswith('_') and ismethod(meth)
            and hasattr(meth, '_ed_events'))
        
        for _, listener in methods:
            events = listener._ed_events
            for event in events:
                self._event_hooks[event.__name__].append(listener)

    async def _dispatch_event(self, event):

        hooks = self._event_hooks[type(event).__name__]

        if not hooks:
            return
        
        async def _hook_wrapper(hook, event):
            await hook(event)

        tasks = [_hook_wrapper(hook, event) for hook in hooks]
        await asyncio.gather(*tasks)
