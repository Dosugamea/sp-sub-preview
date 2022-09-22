from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Meta:
    """A model to represent meta fields of sus file"""

    title: Optional[str] = None
    subttile: Optional[str] = None
    artist: Optional[str] = None
    genre: Optional[str] = None
    designer: Optional[str] = None
    difficulty: Optional[str] = None
    playlevel: Optional[str] = None
    songid: Optional[str] = None
    wave: Optional[str] = None
    waveoffset: Optional[str] = None
    jacket: Optional[str] = None
    background: Optional[str] = None
    movie: Optional[str] = None
    movieoffset: Optional[float] = None
    basebpm: Optional[float] = None
    requests: list = field(default_factory=list)
