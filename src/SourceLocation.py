"""Source coordinates attached to tokens and syntax-tree nodes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceLocation:
    line: int
    column: int
    offset: int

    def __str__(self) -> str:
        return f"line {self.line}, column {self.column}"
