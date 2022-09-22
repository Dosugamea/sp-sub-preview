import re


class Line:
    """A model to represent a line in a sus file"""

    type: str
    header: str
    data: str

    def __init__(self, line: str):
        line = line.strip()

        if match := re.match(r"^#(\w+)\s+(.*)$", line):
            self.type = "meta"
            self.header, self.data = match.groups()

        elif match := re.match(r"^#(\w+):\s*(.*)$", line):
            self.type = "score"
            self.header, self.data = match.groups()

        else:
            self.type = "comment"
            self.header, self.data = "comment", line
