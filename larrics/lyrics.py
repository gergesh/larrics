from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Lyrics:
    unsynchronized: Optional[str] = None
    synchronized: Optional[str] = None

    def __add__(self, other: Lyrics) -> Lyrics:
        return Lyrics(
            self.unsynchronized or other.unsynchronized,
            self.synchronized or other.synchronized,
        )


def strip_timestamps(lrc: str) -> str:
    return re.sub(r'\[[\d\.:]+\] *', '', lrc).strip()


def strip_leading_spaces(lrc: str) -> str:
    return re.sub(r'(\[[\d\.:]+\]) *', r'\g<1>', lrc).strip()
