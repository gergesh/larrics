from ..lyrics import Lyrics


class Provider:
    name = 'provider-name'

    def __init__(self, config_entry):
        raise NotImplementedError()

    def get_lyrics(self, artist: str, title: str, duration: int) -> Lyrics:
        raise NotImplementedError()
