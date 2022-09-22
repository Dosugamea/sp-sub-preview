from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    bar: float
    bpm: float = 0
    bar_length: float = 0
    sentence_length: int = 0
    section: Optional[str] = None
    text: Optional[str] = None

    def __or__(self, other):
        assert self.bar <= other.bar
        return Event(
            bar=other.bar,
            bpm=other.bpm or self.bpm,
            bar_length=other.bar_length or self.bar_length,
            sentence_length=other.sentence_length or self.sentence_length,
            section=other.section or self.section,
            text=other.text or self.text,
        )
