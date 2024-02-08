import os
import logging
import asyncio
import aiohttp

from collections import defaultdict
from typing import TYPE_CHECKING

from .errors import AuthenticationError, RequestError
from .events import (ThreadNewEvent, ThreadUpdateEvent, ThreadDeleteEvent, CommentNewEvent,
                     CommentUpdateEvent, CommentDeleteEvent, CourseCountEvent)
from .models.comment import Comment
from .models.thread import Thread

if TYPE_CHECKING:
    from .client import EdClient

_log = logging.getLogger('edspy.transport')

API_HOST = 'us.edstem.org'

CLOSE_TYPES = (
    aiohttp.WSMsgType.CLOSE,
    aiohttp.WSMsgType.CLOSING,
    aiohttp.WSMsgType.CLOSED
)


class Transport:
    """The class responsible for dealing with connections to Ed client."""

    def __init__(self, client: 'EdClient', ed_token: str) -> None:

        self.client = client
        self.ed_token = ed_token or os.getenv('ED_API_TOKEN')

        self._ws = None
        self._ws_token = None
        self._ws_closed = True

        self._session = aiohttp.ClientSession()
        
        self._message_id = 0
        self._message_queue: list[str] = []
        self._message_sent = defaultdict(dict)

    @property
    def ws_connected(self):
        return self._ws is not None and not self._ws.closed

    async def _get_ws_token(self):
        
        res = await self._request('POST', '/api/renew_token')
        self._ws_token = res['token']
        _log.info('Token renewed successfully.')

    """
    async def close(self):
        if not self._ws:
            return
        
        await self._ws.close(code=aiohttp.WSCloseCode.OK)
        self._ws = None
        self._ws_closed = True
    """

    async def _request(self, method: str, endpoint: str, to=None):

        if not self.ed_token:
            raise RequestError('Ed API token is not provided and cannot be loaded from environment') 

        try:
            async with self._session.request(method=method, url= 'https://{}{}'.format(API_HOST, endpoint),
                                             headers={'Authorization': self.ed_token}) as res:
                
                if (code := res.status) != 200:
                    if code == 400:
                        raise AuthenticationError('Invalid Ed API token.')
                    if code == 403:
                        raise RequestError('Missing permission')
                    if code == 404:
                        raise RequestError('Invalid API endpoint.')

                if to is str:
                    return await res.text()

                json = await res.json()
                return json if to is None else to.from_dict(json)

        except aiohttp.ClientConnectorError:
            pass

    async def _connect(self):

        attempt = 0
        self._ws_closed = False
        while not self.ws_connected and not self._ws_closed:
            attempt += 1
            try:
                self._ws = await self._session.ws_connect(
                    url='wss://{}/api/stream'.format(API_HOST),
                    params={'_token': self._ws_token or ''},
                    heartbeat=60)
            except aiohttp.WSServerHandshakeError as ce:
                if isinstance(ce, aiohttp.WSServerHandshakeError):
                    if ce.status == 401:
                        _log.info('Authentication failed.')
                        if attempt == 10:
                            _log.error('Failed due to unkwown reason.')
                            raise ce
                        _log.info('Attempting to renew token...')
                        await self._get_ws_token()
                    elif ce.status == 503:  # may happen at times
                        pass
                else:
                    _log.error('Failed to connect to websocket with status code {} and\
                        error message "{}".Retrying...'.format(ce.status, ce.message))

                backoff = 5
                await asyncio.sleep(backoff)
            else:
                _log.info('Connection to websocket established.')
                attempt = 0

                if self._message_queue:
                    for message in self._message_queue:
                        await self._send(message)
                    self._message_queue.clear()

                await self._listen()

    async def _send(self, data: dict):

        data['id'] = self._message_id = self._message_id + 1
        self._message_sent[self._message_id] = data
        if not self._ws:
            self._message_queue.append(data)
            return
        await self._ws.send_json(data)

    async def _listen(self):
        """ Listens for websocket messages. """
        close_code = None
        
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self._handle_message(msg.json())
            elif msg.type == aiohttp.WSMsgType.ERROR:
                _log.error('Websocket connection closed with exception %s', self._ws.exception())
                close_code = aiohttp.WSCloseCode.INTERNAL_ERROR
            elif msg.type in CLOSE_TYPES:
                _log.info('Websocket connection closed with [%d] %s', msg.data, msg.extra)
                close_code = msg.data
                break

        close_code = close_code or self._ws.close_code
        _log.warning('WebSocket disconnected with the following: code=%s', close_code)
        if self._ws:
            await self._ws.close(code=close_code or aiohttp.WSCloseCode.OK)
            self._ws = None
        self._ws_closed = True

    async def _handle_message(self, message: dict):
        
        event_type, data = message['type'], message.get('data')
        event = None

        _log.debug('Event: %s - Payload: %s', event_type, data)
        if event_type in ('chat.init', 'course.subscribe'):
            if event_type == 'course.subscribe':
                sent_msg = self._message_sent[message['id']]
                _log.info(f'Course {sent_msg["oid"]} subscribed.')
            return
        
        if event_type == 'thread.new':
            data = data.get('thread')
            thread = Thread(data, **data)
            event = ThreadNewEvent(thread)
            _log.info('Event: %s - Payload: %s', event_type, data)

        elif event_type == 'thread.update':
            data = data.get('thread')
            thread = Thread(data, **data)
            event = ThreadUpdateEvent(thread)
            # _log.info('Event: %s - Payload: %s', event_type, data)

        elif event_type == 'thread.delete': # only id is nontrivial
            thread = Thread(data, id=data.get('thread_id'))     
            event = ThreadDeleteEvent(thread)
            _log.info('Event: %s - Payload: %s', event_type, data)

        elif event_type == 'comment.new':
            data = data.get('comment')
            comment = Comment(data, **data)
            event = CommentNewEvent(comment)
            _log.info('Event: %s - Payload: %s', event_type, data)

        elif event_type == 'comment.update':
            data = data.get('comment')
            comment = Comment(data, **data)
            event = CommentUpdateEvent(comment)
            _log.info('Event: %s - Payload: %s', event_type, data)

        elif event_type == 'comment.delete': # only id and thread_id are nontrivial
            comment = Comment(data, id=data.get('comment_id'), thread_id=data.get('thread_id'))
            event = CommentDeleteEvent(comment)
            _log.info('Event: %s - Payload: %s', event_type, data)

        elif event_type == 'course.count':
            event = CourseCountEvent(data.get('id'), data.get('count'))
            # _log.info('Event: %s - Payload: %s', event_type, data)

        else:
            _log.warning('Uknown event. Event: %s - Payload: %s', event_type, data)
        
        await self.client._dispatch_event(event)
