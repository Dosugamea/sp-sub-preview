from dataclasses import dataclass, field
from typing import Optional

from .note import Note


@dataclass
class Directional(Note):
    """A model to represent directional note"""

    tap: Optional[Note] = field(default=None, repr=False)

    def __hash__(self) -> int:
        return hash(str(self))
