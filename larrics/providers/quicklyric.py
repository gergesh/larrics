import datetime as dt
import hmac
from base64 import b64encode
from hashlib import sha1

import requests

from ..lyrics import Lyrics
from .provider import Provider


class QuickLyric(Provider):
    name = 'quicklyric'
    synchronized = True

    def __init__(self, config_entry):
        self.s = requests.Session()
        self.s.headers.update(
            {'user-agent': 'com.geecko.QuickLyric', 'accept-encoding': 'gzip'}
        )
        self.location = (
            config_entry.get('location')
            or self.s.head('https://api.quicklyric.com').headers['location']
        )
        self.zero_duration = config_entry.getboolean('zero_duration', False)
        self.player = config_entry.get('player', 'com.poupa.vinylmusicplayer')

    def get_lyrics(self, artist: str, title: str, duration: int) -> Lyrics:
        params = [
            ('q_track', title),
            ('q_artist', artist),
            ('q_fingerprint', ''),
            ('q_duration', '0' if self.zero_duration else str(duration)),
            ('q_sag', 'false'),
            ('player', self.player),
            ('v', '4000310'),
        ]
        signature = self._get_signature(
            f'/?{"&".join(f"{k}={v}" for k, v in params)}'.replace(' ', '+'),
            b'a22ddff2b3d447e25705ac779abfcee98e5b8756',
        )
        params.append(('signature', signature))
        params.append(('signature_protocol', 'sha1'))
        j = self.s.get(f'{self.location}matchLyrics', params=params).json()
        return Lyrics(j.get('text'), self._lrc_from_lines(j.get('lines')))

    @staticmethod
    def _get_signature(params: str, hmac_init: bytes) -> bytes:
        now = dt.datetime.now(dt.timezone.utc)
        dat = f'{params}{now.strftime("%Y%m%d")}'
        mac = hmac.new(hmac_init, dat.encode('utf-8'), sha1)
        return b64encode(mac.digest()).rstrip(b'=')

    @staticmethod
    def _lrc_from_lines(lines: []) -> str:
        if not lines:
            return None
        return '\n'.join(f'[{l["timing"]}]{l["text"]}' for l in lines)
