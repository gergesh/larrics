import re
from dataclasses import dataclass
from typing import NamedTuple, Optional


@dataclass
class Lyrics:
    unsynchronized: Optional[str] = None
    synchronized: Optional[str] = None

    def __add__(self, other):
        return Lyrics(
            self.unsynchronized or other.unsynchronized,
            self.synchronized or other.synchronized,
        )


def strip_timestamps(lrc):
    return re.sub(r'\[[\d\.:]+\] *', '', lrc).strip()


def strip_leading_spaces(lrc):
    return re.sub(r'(\[[\d\.:]+\]) *', r'\g<1>', lrc).strip()
