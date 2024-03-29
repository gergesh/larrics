import argparse
import os
from configparser import ConfigParser
from pathlib import Path
from enum import IntFlag
from typing import Tuple

import taglib

from . import lyrics
from .providers.manager import ProvidersManager

class WriteStatus(IntFlag):
    NONE = 0
    UNSYNCHRONIZED = 1
    SYNCHRONIZED = 2
    BOTH = 3

class LyricsFetcher:
    AUDIO_EXTENSIONS = set(['.flac', '.mp3', '.ogg', '.opus', '.m4a'])

    def __init__(self, args):
        config = ConfigParser()
        if not config.read(args.config):
            raise FileNotFoundError(f'Could not read config file at {args.config}')
        self.pm = ProvidersManager(config, args.providers)
        self.force = args.force
        self.verbose = args.verbose
        self.artist = args.artist
        self.use_album_artist = args.use_album_artist

    def get_lyrics(self, artist: str, title: str, duration: int) -> lyrics.Lyrics:
        lrcs = lyrics.Lyrics()
        for provider in self.pm.providers:
            # Skip over providers with only unsynchronized content if we already have it
            if lrcs.unsynchronized and not provider.synchronized:
                continue
            lrcs += provider.get_lyrics(artist, title, duration)
            if lrcs.synchronized:
                break
        return lrcs

    def get_tags(self, audio_file: Path) -> Tuple[str, str, int]:
        f = taglib.File(str(audio_file))
        title = f.tags['TITLE'][0]
        artists = f.tags['ARTIST']
        album_artists = f.tags['ALBUMARTIST']
        if self.artist is not None:
            artist = self.artist
        elif album_artists and self.use_album_artist:
            artist = album_artists[0]
        elif len(artists) == 1:
            artist = artists[0]
        elif len(album_artists) == 1 and album_artists[0] in artists:
            artist = album_artists[0]
        else:
            artist = ', '.join(artists)

        duration = f.length
        f.close()
        return artist, title, duration

    def write_lyrics(self, audio_file: Path, lrcs: lyrics.Lyrics) -> WriteStatus:
        written = WriteStatus.NONE

        lrc_file = audio_file.with_suffix('.lrc')
        if lrcs.synchronized and (self.force or not lrc_file.is_file()):
            audio_file.with_suffix('.lrc').write_text(lrcs.synchronized)
            written |= WriteStatus.SYNCHRONIZED

        if lrcs.unsynchronized:
            f = taglib.File(str(audio_file))
            if self.force or not f.tags.get('LYRICS'):
                f.tags['LYRICS'] = [lrcs.unsynchronized]
                f.save()
                written |= WriteStatus.UNSYNCHRONIZED
            f.close()

        return written

    @staticmethod
    def has_lyrics(audio_file: Path) -> bool:
        return audio_file.with_suffix('.lrc').is_file()

    def operate(self, arg: Path):
        if arg.is_file():
            candidates = (f for f in [arg])
        elif arg.is_dir():
            candidates = (
                f
                for f in arg.glob('**/*')
                if f.is_file()
                and f.suffix in self.AUDIO_EXTENSIONS
                and (self.force or not self.has_lyrics(f))
            )
        else:
            raise FileNotFoundError(f'Could not operate on invalid path {arg}')

        for c in candidates:
            artist, title, duration = self.get_tags(c)
            lrcs = self.get_lyrics(artist, title, duration)
            if lrcs.synchronized and not lrcs.unsynchronized:
                lrcs.unsynchronized = lyrics.strip_timestamps(lrcs.synchronized)
            labels = ['no', 'unsynchronized', 'synchronized', 'both']
            if self.verbose:
                print(
                    f'Found {labels[bool(lrcs.unsynchronized) + bool(lrcs.synchronized) * 2]} lyrics for {title} by {artist}'
                )
            written = self.write_lyrics(c, lrcs)
            if self.verbose:
                print(f'Wrote {labels[written]} lyrics for {title} by {artist}')


def parse_args():
    parser = argparse.ArgumentParser(
        prog='larrics', description='pirate lyrics fetcher'
    )
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-a', '--artist', help='specify artist to use for searching lyrics')
    parser.add_argument(
        "-aa",
        "--use-album-artist",
        action="store_true",
        help="use album artist for searching lyrics",
    )
    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='overwrite existing lyrics with new ones',
    )
    parser.add_argument(
        '-c',
        '--config',
        default=Path(os.getenv('XDG_CONFIG_HOME', Path(os.getenv('HOME')) / '.config'))
        / 'larrics.ini',
        help='configuration file to use',
    )
    parser.add_argument('-p', '--providers', help='list of providers to use', nargs='*')
    parser.add_argument('path', nargs='+')
    return parser.parse_args()


def main():
    args = parse_args()
    lf = LyricsFetcher(args)
    for arg in args.path:
        lf.operate(Path(arg))


if __name__ == '__main__':
    main()
