from dataclasses import dataclass
from .Token import Token, TokenType


KEYWORDS = {"if", "else", "loop", "from", "to", "step", "log", "true", "false"}


@dataclass
class Lexer:
    source: str
    position: int = 0
    line: int = 1

    def current_char(self) -> str | None:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]


    def advance(self) -> None:
        if self.current_char() == "\n":
            self.line += 1
        self.position += 1


    def skip_spaces(self) -> None:
        while self.current_char() in (" ", "\t"):
            self.advance()

    def is_digit(self, char: str) -> bool:
        return "0" <= char <= "9"


    def read_word(self) -> Token:
        start = self.position
        token_line = self.line

        while self.current_char() is not None:
            char = self.current_char()
            if not (char.isalnum() or char == "_"):
                break
            self.advance()

        value = self.source[start:self.position]
        token_type = TokenType.KEYWORD if value in KEYWORDS else TokenType.IDENTIFIER
        return Token(token_type, value, token_line, start)


    def read_number(self) -> Token:
        start = self.position
        token_line = self.line

        while self.current_char() is not None and self.is_digit(self.current_char()):
            self.advance()

        # keeping track of the decimal point correctly
        if self.current_char() == ".":
            self.advance()
            if self.current_char() is None or not self.is_digit(self.current_char()):
                raise ValueError(
                    f"Malformed number on line {token_line}, position {start}: "
                    "a decimal point must be followed by digits"
                )

            while self.current_char() is not None and self.is_digit(self.current_char()):
                self.advance()

        value = self.source[start:self.position]
        return Token(TokenType.NUMBER, value, token_line, start)

    def read_string(self) -> Token:
        start = self.position
        token_line = self.line
        self.advance()  # start after the opening quote
        content_start = self.position

        while self.current_char() is not None and self.current_char() != '"':
            if self.current_char() == "\n":
                raise ValueError(
                    f"String opened on line {token_line}, position {start} "
                    "was not closed before the newline"
                )
            self.advance()

        if self.current_char() is None:
            raise ValueError(
                f"String opened on line {token_line}, position {start} "
                "was not closed before the end of the source"
            )

        value = self.source[content_start:self.position]
        self.advance()  # consume the closing quote
        return Token(TokenType.STRING, value, token_line, start)

    def read_operator(self) -> Token:
        start = self.position
        token_line = self.line
        first = self.current_char()
        self.advance()
        second = self.current_char()

        # These operators can be followed by '=' to make a two-character one.
        if first in ("=", "!", "<", ">") and second == "=":
            self.advance()

        # AND and OR must use two matching characters: && and ||.
        elif first == "&":
            if second != "&":
                raise ValueError(
                    f"Expected '&&' on line {token_line}, position {start}"
                )
            self.advance()
        elif first == "|":
            if second != "|":
                raise ValueError(
                    f"Expected '||' on line {token_line}, position {start}"
                )
            self.advance()

        value = self.source[start:self.position]
        return Token(TokenType.OPERATOR, value, token_line, start)


    def tokenize(self) -> list[Token]:
        tokens = []
        punctuation = {
            "(": TokenType.L_PAREN,
            ")": TokenType.R_PAREN,
            "{": TokenType.L_BRACE,
            "}": TokenType.R_BRACE,
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
        }
        operator_starts = "+-*/%^=!<>&|"

        while self.current_char() is not None:
            char = self.current_char()
            if char in (" ", "\t"):
                self.skip_spaces()

            elif char == "\n":
                tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.position))
                self.advance()

            elif char.isalpha() or char == "_":
                tokens.append(self.read_word())

            elif self.is_digit(char):
                tokens.append(self.read_number())

            elif char == '"':
                tokens.append(self.read_string())

            elif char in punctuation:
                tokens.append(Token(punctuation[char], char, self.line, self.position))
                self.advance()

            elif char in operator_starts:
                tokens.append(self.read_operator())

            else:
                raise ValueError(
                    f"Unexpected character {char!r} on line {self.line}, "
                    f"position {self.position}"
                )

        return tokens

