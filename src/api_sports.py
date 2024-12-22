import json
import logging
import os
import threading
import time

from aiohttp import ClientSession


# Source: https://gist.github.com/benhoyt/8c8a8d62debe8e5aa5340373f9c509c7
# https://gist.github.com/benhoyt/8c8a8d62debe8e5aa5340373f9c509c7?permalink_comment_id=3142969#gistcomment-3142969
class AtomicCounter(object):
    """An atomic, thread-safe counter"""

    def __init__(self, initial=0):
        """Initialize a new atomic counter to given initial value"""
        self._value = initial
        self._lock = threading.Lock()

    def inc(self, num=1) -> int:
        """Atomically increment the counter by num and return the new value"""
        with self._lock:
            self._value += num
            return self._value

    def dec(self, num=1) -> int:
        """Atomically decrement the counter by num and return the new value"""
        with self._lock:
            self._value -= num
            return self._value

    @property
    def value(self):
        return self._value


class APISports:
    API_HOST = 'v3.football.api-sports.io'
    BASE_URL = f'https://{API_HOST}'
    HEADERS = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': os.getenv('API_SPORTS_API_KEY')
    }
    TPM = 10

    def __init__(self):
        assert self.HEADERS['x-rapidapi-key']
        self.req_count = AtomicCounter(initial=1)

    async def get_fixtures(self, client: ClientSession, team: int, season: int) -> list[dict]:
        url = f'{self.BASE_URL}/fixtures?team={team}&season={season}'
        return await self._make_non_paging_request(client, url)

    async def _make_non_paging_request(self, client: ClientSession, url: str) -> list[dict]:
        async with client.get(url, headers=self.HEADERS) as r:
            self._check_tps()
            logging.info(f'About to make non-paging request: url={url}')
            if r.status < 200 or r.status > 299:
                logging.info(f'Received NON 200 response: status code={r.status}, url={url}')
                return []
            rj = await r.json()
            if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                logging.debug(
                    f'Received response: url={url}, status code={r.status}, response headers={r.headers}, response payload=')
                logging.debug(json.dumps(rj, indent=2))
            if rj['paging']['total'] > 1:
                raise Exception('Unexpected response from a non paging request (make a paging request instead?)')
            response = rj['response']
            return response

    def _check_tps(self) -> None:
        counter = 0
        while self.req_count.value % self.TPM == 0 and counter <= 60:
            logging.info(f'RATE LIMIT: Sleeping 1 minute because {self.TPM} transactions per minute hit')
            time.sleep(1)
            counter += 1
        self.req_count.inc()
