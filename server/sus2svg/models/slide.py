from dataclasses import dataclass, field
from typing import Optional

from .note import Note


@dataclass
class Slide(Note):
    """A model to represent slide start/path/end note"""

    channel: int = 0

    tap: Optional[Note] = field(default=None, repr=False)
    directional: Optional[Note] = field(default=None, repr=False)
    next: Optional["Note"] = field(default=None, repr=False)
    head: Optional[Note] = field(default=None, repr=False)

    def __hash__(self) -> int:
        return hash(str(self))

    def is_path_note(self):
        if self.type == 0:
            return False

        if self.type != 3 or self.directional:
            return True

        return self.tap is None and self.directional is None

    def is_among_note(self):
        return self.type == 3
