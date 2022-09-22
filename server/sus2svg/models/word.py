from dataclasses import dataclass


@dataclass
class Word:
    """A model to represent word rendered in svg"""

    bar: float
    text: str
