"""Node types used by the parser to represent source programs as a tree."""

from dataclasses import dataclass


class Expression:
    """Base class for expressions that produce a value."""


class Statement:
    """Base class for statements that perform an action."""


@dataclass
class Program:
    statements: list[Statement]


@dataclass
class Identifier(Expression):
    value: str


@dataclass
class Literal(Expression):
    value: str
    kind: str  # "number", "string", or "bool"


@dataclass
class Unary(Expression):
    operator: str
    operand: Expression


@dataclass
class Binary(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class Assignment(Statement):
    targets: list[Identifier]
    values: list[Expression]


@dataclass
class Log(Statement):
    expression: Expression


@dataclass
class If(Statement):
    condition: Expression
    then_body: list[Statement]
    else_body: list[Statement] | None = None


@dataclass
class Loop(Statement):
    variable: str
    start: Expression
    end: Expression
    step: Expression | None
    body: list[Statement]
