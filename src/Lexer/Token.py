from dataclasses import dataclass
from enum import Enum

from SourceLocation import SourceLocation


class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    OPERATOR = "OPERATOR"
    KEYWORD = "KEYWORD"

    #symbols
    L_PAREN = "L_PAREN"
    R_PAREN = "R_PAREN"
    L_BRACE = "L_BRACE"
    R_BRACE = "R_BRACE"
    COMMA = "COMMA"
    COLON = "COLON"
    NEWLINE = "NEWLINE"

@dataclass
class Token:
    type: TokenType
    value: str
    location: SourceLocation

    @property
    def line(self) -> int:
        return self.location.line

    @property
    def column(self) -> int:
        return self.location.column

    @property
    def position(self) -> int:
        return self.location.offset

    def __str__(self):
        return (
            f"Token [{self.type.name} | {self.value!r} | "
            f"at {self.location}]"
        )






