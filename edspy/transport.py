import os
import logging
import asyncio
import aiohttp

from collections import defaultdict
from typing import TYPE_CHECKING

from .errors import AuthenticationError, RequestError
from .events import ThreadNewEvent, ThreadUpdateEvent
from .models import Course, Thread

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
        self.ed_token = ed_token or os.environ['ED_API_TOKEN']

        self._token = None
        self._ws = None

        self._session = aiohttp.ClientSession()
        
        self._message_id = 0
        self._message_queue: list[str] = []
        self._message_sent = defaultdict(dict)

    async def _login(self):
        
        res = await self._request('POST', '/api/renew_token')
        self._token = res['token']
        _log.info('Token renewed successfully.')

    async def _request(self, method: str, endpoint: str, to=None):
        try:
            async with self._session.request(method=method, url= 'https://{}{}'.format(API_HOST, endpoint),
                                             headers={'Authorization': self.ed_token}) as res:
                
                if code := res.status != 200:
                    if code == 400:
                        raise AuthenticationError('Invalid Ed API token')
                    if code == 404:
                        raise RequestError('Invalid API endpoint')

                if to is str:
                    return await res.text()

                json = await res.json()
                return json if to is None else to.from_dict(json)

        except aiohttp.ClientConnectorError:
            pass

    async def _connect(self):

        attempt = 0
        while not self._ws:
            attempt += 1
            try:
                self._ws = await self._session.ws_connect(
                    url='wss://{}/api/stream'.format(API_HOST),
                    params={'_token': self._token or ''},
                    heartbeat=60)
            except aiohttp.WSServerHandshakeError as ce:
                if isinstance(ce, aiohttp.WSServerHandshakeError):
                    if ce.status == 401:
                        _log.info('Authentication failed.')
                        if attempt == 10:
                            _log.error('Failed due to unkwown reason.')
                            raise ce
                        _log.info('Attempting to renew token...')
                        await self._login()
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
        
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self._handle_message(msg.json())
            elif msg.type == aiohttp.WSMsgType.ERROR:
                _log.error('Websocket connection closed with exception %s', self._ws.exception())
            elif msg.type in CLOSE_TYPES:
                _log.info('Websocket connection closed with [%d] %s', msg.data, msg.extra)
                break

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
            course = Course(next(filter(
                lambda x: x['course']['id'] == data['thread']['course_id'],
                self.client.user_courses)).get('course'))
            thread = Thread(data.get('thread'))
            event = ThreadNewEvent(thread, course)

        elif event_type == 'thread.update':
            thread = Thread(data.get('thread'))
            event = ThreadUpdateEvent(thread)

        else:
            return
        
        await self.client._dispatch_event(event)
