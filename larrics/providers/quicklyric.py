import json
import re
import time

import requests
import urllib3

from ..lyrics import Lyrics, strip_timestamps
from .provider import Provider

# QuickLyric's certificate is invalid and requests keeps complaining about it
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class QuickLyric(Provider):
    name = 'quicklyric'

    def __init__(self, config_entry):
        self.token = config_entry['token']

    def get_lyrics(self, artist: str, title: str, duration: int) -> Lyrics:
        url = 'https://api.quicklyric.be/get?lrc=true'
        headers = {
            'User-Agent': 'com.geecko.QuickLyric',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        payload = {
            'q': '\n'.join(
                [artist, title, str(int(time.time() * 1000)), '4000260', self.token,]
            ),
            'v': '4000260',
            'p': 'com.poupa.vinylmusicplayer',
            'au': 'false',
            'sag': 'true',
        }

        if duration:
            payload['d'] = str(duration)
        r = requests.post(url, headers=headers, data=payload, verify=False)
        if r.status_code != 200:
            raise Exception('QuickLyric: Got a non-200 status code')

        js = json.loads(r.text)
        lyrics = Lyrics()
        if js['code'] != 200:
            return lyrics
        if js['LRC']:  # Synchronized lyrics
            return Lyrics(strip_timestamps(js['text']), js['text'])
        else:
            return Lyrics(self.txt_from_html(js['text']), None)

    _re_multiple_newlines = re.compile(r'\n{2,}')
    _re_trailing_spaces = re.compile(r'\s+\n')
    _re_html_newline = re.compile(r'<(br|p)>')
    _re_html_tag = re.compile(r'</?\w+>')

    @classmethod
    def txt_from_html(cls, x):
        x = cls._re_html_newline.sub('\n', x)
        x = cls._re_html_tag.sub('', x)
        x = cls._re_multiple_newlines.sub('\n', x)
        x = cls._re_trailing_spaces.sub('\n', x)
        return x.strip()
