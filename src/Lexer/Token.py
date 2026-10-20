from dataclasses import dataclass
from enum import Enum

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
    line: int
    position:int

    def __str__(self):
        return f"Token [{self.type} | {self.value} | at Line={self.line} | Position={self.position}]"






