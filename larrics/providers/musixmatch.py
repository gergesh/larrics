import contextlib
import datetime
import hmac
from base64 import b64encode
from hashlib import sha1
from urllib.parse import urlencode

import requests

from ..lyrics import Lyrics, strip_leading_spaces
from .provider import Provider


class MusixMatch(Provider):
    name = 'musixmatch'
    synchronized = True

    def __init__(self, config_entry):
        self.token = config_entry['token']

    def get_lyrics(self, artist: str, title: str, duration: int) -> Lyrics:
        url = 'https://apic.musixmatch.com/ws/1.1/macro.subtitles.get'
        params = {
            'tags': 'playing',
            'subtitle_format': 'lrc',
            'q_track': title,
            'q_artist': artist,
            'usertoken': self.token,
            'app_id': 'android-player-v1.0',
            'country': 'us',
            'f_subtitle_length_max_deviation': 1,
            'language_iso_code': 1,
            'page_size': '1',
            'part': 'track_artist,artist_image,lyrics_crowd,user,lyrics_vote,lyrics_poll,track_lyrics_translation_status,lyrics_verified_by,',
            'format': 'json',
            'optional_calls': 'track.richsync',
        }

        if duration:
            params['q_duration'] = params['f_subtitle_length'] = duration

        # Sign request
        newrl = f'{url}?{urlencode(params)}'
        bytes1 = f'{newrl}{datetime.date.today().strftime("%Y%m%d")}'.encode()
        bytes2 = b"967Pn4)N3&R_GBg5$b('"
        signature = b64encode(hmac.new(bytes2, bytes1, sha1).digest())
        newrl += '&' + urlencode({'signature': signature}) + '&signature_protocol=sha1'

        js = requests.get(newrl).json()

        if js['message']['header']['status_code'] == 401:
            raise Exception('MusixMatch: Got a 401 response')

        lyrics = Lyrics()
        with contextlib.suppress(KeyError, TypeError):
            lyrics.synchronized = strip_leading_spaces(
                js['message']['body']['macro_calls']['track.subtitles.get']['message'][
                    'body'
                ]['subtitle_list'][0]['subtitle']['subtitle_body']
            )
        with contextlib.suppress(KeyError, TypeError):
            lyrics.unsynchronized = js['message']['body']['macro_calls'][
                'track.lyrics.get'
            ]['message']['body']['lyrics']['lyrics_body']

        return lyrics
