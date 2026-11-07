"""Node types used by the parser to represent source programs as a tree."""

from dataclasses import dataclass

from SourceLocation import SourceLocation


class Expression:
    """Base class for expressions that produce a value."""


class Statement:
    """Base class for statements that perform an action."""


@dataclass
class Program:
    statements: list[Statement]
    location: SourceLocation | None = None


@dataclass
class Identifier(Expression):
    value: str
    location: SourceLocation


@dataclass
class Literal(Expression):
    value: str
    kind: str  # "number", "string", or "bool"
    location: SourceLocation


@dataclass
class Unary(Expression):
    operator: str
    operand: Expression
    location: SourceLocation


@dataclass
class Binary(Expression):
    left: Expression
    operator: str
    right: Expression
    location: SourceLocation


@dataclass
class Assignment(Statement):
    targets: list[Identifier]
    values: list[Expression]
    location: SourceLocation


@dataclass
class Log(Statement):
    expression: Expression
    location: SourceLocation


@dataclass
class If(Statement):
    condition: Expression
    then_body: list[Statement]
    location: SourceLocation
    else_body: list[Statement] | None = None


@dataclass
class Loop(Statement):
    variable: str
    start: Expression
    end: Expression
    step: Expression | None
    body: list[Statement]
    location: SourceLocation
