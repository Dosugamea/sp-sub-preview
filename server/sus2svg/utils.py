import re

from models import Word


def load_lyric(lines: list[str]) -> list[Word]:
    words: list[Word] = []
    for line in lines:
        line = line.strip()
        if match := re.match(r"^(\d+): (.*)$", line):
            bar = int(match.group(1))
            texts = match.group(2).split("/")
            for i, text in enumerate(texts):
                if text:
                    words.append(Word(bar=bar + i / len(texts), text=text))
    return words


def get_denominator(x: float) -> int:
    ans: int = 1000
    remainder: float = 1000

    for y in [
        1,
        2,
        4,
        8,
        16,
        32,
        64,
        3,
        6,
        12,
        24,
        48,
        96,
        5,
        10,
        20,
        40,
        80,
    ]:
        r = min((x * y) % 1, (-x * y) % 1)
        if r < remainder:
            ans, remainder = y, r
        if r < remainder + 1e-3 and y < ans:
            ans, remainder = y, r

    return ans
