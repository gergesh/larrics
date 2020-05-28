from configparser import ConfigParser
from typing import List

from .genius import Genius
from .musixmatch import MusixMatch
from .provider import Provider
from .quicklyric import QuickLyric


class ProvidersManager:
    def __init__(self, config: ConfigParser, providers: List[str] = None):
        mapping = {p.name: p for p in Provider.__subclasses__()}
        self.providers = []
        for p in providers or config.sections():
            try:
                self.providers.append(mapping[p](config[p]))
            except KeyError as e:
                raise KeyError(
                    f'Provider {p} missing parameters or not found in config file'
                ) from e
