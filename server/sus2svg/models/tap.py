from dataclasses import dataclass

from .note import Note


@dataclass
class Tap(Note):
    """A model to represent simple tap note"""

    def __hash__(self) -> int:
        return hash(str(self))
