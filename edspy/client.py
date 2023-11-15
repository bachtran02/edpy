import os
import asyncio
import aiohttp
import base64
import pickle
import logging

from collections import defaultdict
from inspect import getmembers, ismethod
from urllib.parse import urlparse, parse_qs

from .events import Event, ThreadNewEvent, ThreadUpdateEvent

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

UNI_SUFFIX = 'berkeley.edu'
API_HOST = 'us.edstem.org/api'
BASE_LOGIN_URL = 'https://edstem.org/us/login'

PICKLE_FILE = 'token.pkl'

_log = logging.getLogger(__name__)


def listener(*events: Event):
    def wrapper(func):
        setattr(func, '_ed_events', events)
        return func
    return wrapper

class EdClient():

    def __init__(self, username=None, password=None) -> None:

        self.username = username or os.environ['USERNAME']
        self.password = password or os.environ['PASSWORD']
        
        self.token = None
        self.ws_token = None
        self._ws = None
        self._session = aiohttp.ClientSession()

        self._event_hooks = defaultdict(list)
        
        self._message_id = 0
        self._message_queue: list[str] = []
        self._message_sent = defaultdict(dict)

        self._load_cache()

    async def subscribe(self, course_ids: list = []):

        for course_id in course_ids:

            if not (isinstance(course_id, int) or course_id.isdigit()):
                raise ValueError('Course ID must be integer or integer-like string')
            self._message_id += 1
            await self._send({'id': self._message_id, 'type': 'course.subscribe', 'oid': int(course_id)})
    
        await self._connect()

    def add_event_hooks(self, cls):
        
        methods = getmembers(cls, predicate=lambda meth: hasattr(meth, '__name__')
            and not meth.__name__.startswith('_') and ismethod(meth)
            and hasattr(meth, '_ed_events'))
        
        for _, listener in methods:
            events = listener._ed_events
            for event in events:
                self._event_hooks[event.__name__].append(listener)

    def _load_cache(self):
        try:
            with open(PICKLE_FILE, 'rb') as f:
                data = pickle.load(f)
                self.token, self.ws_token = data.get('token'), data.get('ws_token')
        except FileNotFoundError as e:
            _log.info('Pickle file doesn\'t exist.')

    def _cache(self):
        data = {'token': self.token, 'ws_token': self.ws_token}
        with open(PICKLE_FILE, 'wb') as f:
            pickle.dump(data, f)

    def _login(self):

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(
            options=options,
            seleniumwire_options={'disable_encoding': True})
        
        # edstem login
        driver.get(BASE_LOGIN_URL)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.ID, 'x1'))).send_keys(F'_@{UNI_SUFFIX}')
        driver.find_element(By.CLASS_NAME, 'start-btn').click()
        
        # calcentral login
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'loginForm')))
        driver.find_element(By.ID, 'username').send_keys(self.username)
        driver.find_element(By.ID, 'password').send_keys(self.password)
        driver.find_element(By.ID, 'submit').click()

        try:
            _log.info('Please verify login attempt via Duo...')
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(
                (By.ID, 'dont-trust-browser-button'))).click()
        except TimeoutError as e:
            driver.close()
            _log.error('Duo 2-Step Authentication failed!')
            raise e('Failed to verify Duo 2-Step Authentication')

        # successfully logged in 
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'dash-courses')))
        
        for request in driver.requests:
            if request.url == f'https://{API_HOST}/renew_token':
                self.token = request.headers['x-token']
            if request.url.startswith(f'wss://{API_HOST}/stream'):
                parsed = urlparse(request.url)
                self.ws_token = parse_qs(parsed.query)['_token'][0]
        driver.close()
        self._cache()

    async def _connect(self):

        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "Upgrade",
            "Host": 'us.edstem.org',
            "Origin": "https://edstem.org",
            "Pragma": "no-cache",
            "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-Websocket-Key": self.generate_websocket_key(),
            "Sec-Websocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        }

        attempt = 0
        while not self._ws:
            attempt += 1
            try:
                self._ws = await self._session.ws_connect(
                    url=f'wss://{API_HOST}/stream',
                    params={'_token': self.ws_token or ''},
                    headers=headers, heartbeat=60)
            except aiohttp.WSServerHandshakeError as ce:
                if isinstance(ce, aiohttp.WSServerHandshakeError):
                    if ce.status == 401:
                        _log.info('Authentication failed. Trying to log in...')
                        self._login()
                    elif ce.status == 503:  # may happen at times
                        pass
                else:
                    _log.error('Failed to connect to websocket with status code {} and\
                        error message "{}".Retrying...'.format(ce.status, ce.message))

                backoff = min(10 * attempt, 60)
                await asyncio.sleep(backoff)
            else:
                _log.info('Connection to websocket established!')
                
                if self._message_queue:
                    for message in self._message_queue:
                        await self._send(message)

                    self._message_queue.clear()

                attempt = 0
                await self._listen()

    async def _send(self, data: dict):

        self._message_sent[data['id']] = data
        if not self._ws:
            self._message_queue.append(data)
            return
        await self._ws.send_json(data)

    async def _listen(self):
        
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self._handle_message(msg.json())
            elif msg.type == aiohttp.WSMsgType.ERROR:
                pass

    async def _handle_message(self, message: dict):
        
        event_type, data = message['type'], message.get('data')
        event = None
        
        if event_type == 'course.subscribe':
            sent_msg = self._message_sent[message['id']]
            _log.info(f'Course {sent_msg["oid"]} subscribed successfully!')
            return
        if event_type == 'thread.new':
            event = ThreadNewEvent(data.get('thread'))
        elif event_type == 'thread.update':
            event = ThreadUpdateEvent(data.get('thread'))
        else:
            return
        
        await self._dispatch_event(event)

    async def _dispatch_event(self, event):

        hooks = self._event_hooks[type(event).__name__]

        if not hooks:
            return
        
        async def _hook_wrapper(hook, event):
            await hook(event)

        tasks = [_hook_wrapper(hook, event) for hook in hooks]
        await asyncio.gather(*tasks)

    @staticmethod
    def generate_websocket_key():
        random_bytes = os.urandom(16)
        return base64.b64encode(random_bytes).decode('utf-8')
