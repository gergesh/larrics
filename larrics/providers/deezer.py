from pydeezer import Deezer as PyDeezer

from ..lyrics import Lyrics
from .provider import Provider


class Deezer(Provider):
    name = "deezer"
    synchronized = True

    def __init__(self, config_entry):
        self.client = PyDeezer(arl=config_entry["arl"])

    def get_lyrics(self, artist: str, title: str, _: int) -> Lyrics:
        lyrics = Lyrics()
        tracks = self.client.search_tracks(f"{artist} {title}")
        tracks = [
            t for t in tracks if t["title"] == title and t["artist"]["name"] == artist
        ]

        if tracks:
            track_lyrics = self.client.get_track_lyrics(tracks[0]["id"])["info"]
            lyrics.unsynchronized = track_lyrics.get("LYRICS_TEXT")
            if lyrics.unsynchronized:
                lyrics.unsynchronized = lyrics.unsynchronized.replace("\r\n", "\n")
            if lyrics_sync_json := track_lyrics.get("LYRICS_SYNC_JSON"):
                lyrics_sync_json = [x for x in lyrics_sync_json if x.get("line")]
                lyrics_sync_json.sort(key=lambda x: int(x["milliseconds"]))
                lyrics.synchronized = "".join(
                    f"{line['lrc_timestamp']} {line['line']}\n"
                    for line in lyrics_sync_json
                )

        return lyrics
