import re
from enum import Enum
from typing import Optional


class Emoji(Enum):
    """Class to refactor custom emojis used in the server."""

    CHECK = "check"
    LEFT = "arrowleft"
    RIGHT = "arrowright"
    UP = "arrowup"
    DOWN = "arrowdown"
    HINT = "hint"
    CROSS = "exit"
    A = "letter_a"
    B = "letter_b"
    C = "letter_c"
    D = "letter_d"
    E = "letter_e"
    F = "letter_f"

    @classmethod
    def from_pattern(cls, pattern: str) -> Optional["Emoji"]:
        """Convert <:name:id> pattern to Emoji enum."""
        match = re.match(r"<:(\w+):\d+>", pattern)
        if match:
            emoji_name = match.group(1)
            return cls.get_enum_name(emoji_name)
        return None

    @classmethod
    def get_enum_name(cls, name: str) -> Optional["Emoji"]:
        """Get the Emoji enum member by its name."""
        for emoji in cls:
            if emoji.value == name:
                return emoji
        return None

    @classmethod
    def replace_custom_emojis(cls, text: str) -> str:
        """Replace custom emojis in the text with Emoji enum names."""

        def emoji_replacer(match: re.Match) -> str:
            emoji = cls.from_pattern(match.group(0))
            if emoji:
                return f":{emoji.name}:"
            return match.group(0)

        emoji_pattern = re.compile(r"<:(\w+):\d+>")
        return emoji_pattern.sub(emoji_replacer, text)
