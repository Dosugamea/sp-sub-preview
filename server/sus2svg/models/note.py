from dataclasses import dataclass


@dataclass
class Note:
    """A base model to represent note (every note class inherits from this)"""

    bar: float
    lane: int
    width: int
    type: int

    def __hash__(self) -> int:
        return hash(str(self))
