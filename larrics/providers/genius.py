from lyricsgenius import Genius as LyrGenius

from ..lyrics import Lyrics
from .provider import Provider


class Genius(Provider):
    name = 'genius'

    def __init__(self, config_entry):
        remove_section_headers = config_entry.getboolean(
            'remove_section_headers', False
        )
        self.genius = LyrGenius(
            config_entry['token'],
            verbose=False,
            remove_section_headers=remove_section_headers,
        )

    def get_lyrics(self, artist: str, title: str, _: int) -> Lyrics:
        lyrics = Lyrics()
        song = self.genius.search_song(title, artist, get_full_info=False)
        if song:
            lyrics.unsynchronized = song.lyrics
        return lyrics
