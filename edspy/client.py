import asyncio

from collections import defaultdict
from inspect import getmembers, ismethod

from .transport import Transport

class EdClient():

    def __init__(self, ed_token: str = None) -> None:

        self._event_hooks = defaultdict(list)
        self._transport = Transport(self, ed_token)

        self.user, self.user_courses = None, None

    async def subscribe(self, course_ids: list = []):

        for course_id in course_ids:

            if not (isinstance(course_id, int) or course_id.isdigit()):
                raise ValueError('Course ID must be integer or integer-like string')
            
            await self._transport._send({'type': 'course.subscribe', 'oid': int(course_id)})

        await self._get_user()
        await self._transport._connect()

    async def _get_user(self):
        
        res = await self._transport._request('GET', '/api/user')
        self.user = res.get('user')
        self.user_courses = res.get('courses')

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
