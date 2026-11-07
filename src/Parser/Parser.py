from Lexer.Token import Token, TokenType
from .AST import (
    Assignment,
    Binary,
    Expression,
    If,
    Identifier,
    Literal,
    Log,
    Loop,
    Program,
    Statement,
    Unary,
)


class ParserError(SyntaxError):
    """A syntax error found while reading the token stream."""


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.position = 0

    def current_token(self) -> Token | None:
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]

    def advance(self) -> Token | None:
        token = self.current_token()
        if token is not None:
            self.position += 1
        return token

    def match(self, token_type: TokenType, value: str | None = None) -> Token | None:
        token = self.current_token()
        if token is None or token.type != token_type:
            return None
        if value is not None and token.value != value:
            return None
        return self.advance()

    def expect(self, token_type: TokenType, value: str | None = None) -> Token:
        token = self.match(token_type, value)
        if token is not None:
            return token

        found = self.current_token()
        expected = token_type.name if value is None else repr(value)
        if found is None:
            raise ParserError(f"Expected {expected}, but reached the end of the input")

        raise ParserError(
            f"Expected {expected}, found {found.value!r} "
            f"at {found.location}"
        )

    def skip_newlines(self) -> None:
        while self.match(TokenType.NEWLINE) is not None:
            pass

    def parse_program(self) -> Program:
        """Parse all top-level statements and return the program root node."""
        statements: list[Statement] = []
        self.skip_newlines()

        while self.current_token() is not None:
            statements.append(self.parse_statement())

            # A newline separates statements; end-of-input may end the last one.
            if self.current_token() is None:
                break
            self.expect(TokenType.NEWLINE)
            self.skip_newlines()

        location = statements[0].location if statements else None
        return Program(statements, location)

    def parse_statement(self) -> Statement:
        token = self.current_token()
        if token is None:
            raise ParserError("Expected a statement, but reached the end of the input")

        if token.type == TokenType.KEYWORD and token.value == "log":
            return self.parse_log()

        if token.type == TokenType.KEYWORD and token.value == "if":
            return self.parse_if()

        if token.type == TokenType.KEYWORD and token.value == "loop":
            return self.parse_loop()

        if token.type == TokenType.IDENTIFIER:
            return self.parse_assignment()

        raise ParserError(
            f"Expected an assignment, log, if, or loop statement, found {token.value!r} "
            f"at {token.location}"
        )

    def parse_assignment(self) -> Assignment:
        # Parse an assignment statement in the form => identifier [, identifier]* = expression [, expression]*
        first_target = self.expect(TokenType.IDENTIFIER)
        targets = [Identifier(first_target.value, first_target.location)]

        while self.match(TokenType.COMMA) is not None:
            target = self.expect(TokenType.IDENTIFIER)
            targets.append(Identifier(target.value, target.location))

        self.expect(TokenType.OPERATOR, "=")

        values = [self.parse_expression()]
        while self.match(TokenType.COMMA) is not None:
            values.append(self.parse_expression())

        if len(targets) != len(values):
            raise ParserError(
                f"Assignment has {len(targets)} target(s) but {len(values)} value(s) "
                f"at {first_target.location}"
            )

        return Assignment(targets, values, first_target.location)

    def parse_log(self) -> Log:
        # Parse a log statement in the form => log: expression
        log_token = self.expect(TokenType.KEYWORD, "log")
        self.expect(TokenType.COLON)
        expression = self.parse_expression()
        return Log(expression, log_token.location)

    def parse_block(self) -> list[Statement]:
        """Parse statements between braces and return them as a list."""
        self.expect(TokenType.L_BRACE)
        statements: list[Statement] = []
        self.skip_newlines()

        while (
            self.current_token() is not None
            and self.current_token().type != TokenType.R_BRACE
        ):
            statements.append(self.parse_statement())

            # The closing brace can end the final statement in the block.
            token = self.current_token()
            if token is None or token.type == TokenType.R_BRACE:
                break

            self.expect(TokenType.NEWLINE)
            self.skip_newlines()

        self.expect(TokenType.R_BRACE)
        return statements

    def parse_if(self) -> If:
        """Parse if (condition) { ... }, with optional else or else if."""
        if_token = self.expect(TokenType.KEYWORD, "if")
        self.expect(TokenType.L_PAREN)
        condition = self.parse_expression()
        self.expect(TokenType.R_PAREN)
        then_body = self.parse_block()

        else_body: list[Statement] | None = None

        # An else belongs to this if even if newlines appear before it. Only
        # move the real cursor past those newlines when an else is actually there.
        else_position = self.position
        while (
            else_position < len(self.tokens)
            and self.tokens[else_position].type == TokenType.NEWLINE
        ):
            else_position += 1

        if (
            else_position < len(self.tokens)
            and self.tokens[else_position].type == TokenType.KEYWORD
            and self.tokens[else_position].value == "else"
        ):
            self.position = else_position
            self.advance()  # consume 'else'
            if (
                self.current_token() is not None
                and self.current_token().type == TokenType.KEYWORD
                and self.current_token().value == "if"
            ):
                else_body = [self.parse_if()]
            else:
                else_body = self.parse_block()

        return If(condition, then_body, if_token.location, else_body)

    def parse_loop(self) -> Loop:
        """Parse loop name from start to end [step amount] { body }."""
        
        loop_token = self.expect(TokenType.KEYWORD, "loop")
        variable = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.KEYWORD, "from")
        start = self.parse_expression()
        self.expect(TokenType.KEYWORD, "to")
        end = self.parse_expression()

        step = None
        if self.match(TokenType.KEYWORD, "step") is not None:
            step = self.parse_expression()

        body = self.parse_block()
        return Loop(variable, start, end, step, body, loop_token.location)

    def parse_expression(self) -> Expression:
        """Start expression parsing at the lowest-precedence operator level."""
        return self.parse_or()

    def parse_or(self) -> Expression:
        expression = self.parse_and()
        while True:
            operator = self.match(TokenType.OPERATOR, "||")
            if operator is None:
                return expression
            right = self.parse_and()
            expression = Binary(expression, operator.value, right, operator.location)

    def parse_and(self) -> Expression:
        expression = self.parse_equality()
        while True:
            operator = self.match(TokenType.OPERATOR, "&&")
            if operator is None:
                return expression
            right = self.parse_equality()
            expression = Binary(expression, operator.value, right, operator.location)

    def parse_equality(self) -> Expression:
        expression = self.parse_comparison()
        while True:
            operator = self.current_token()
            if (
                operator is None
                or operator.type != TokenType.OPERATOR
                or operator.value not in ("==", "!=")
            ):
                return expression
            self.advance()
            right = self.parse_comparison()
            expression = Binary(expression, operator.value, right, operator.location)

    def parse_comparison(self) -> Expression:
        expression = self.parse_term()
        while True:
            operator = self.current_token()
            if (
                operator is None
                or operator.type != TokenType.OPERATOR
                or operator.value not in ("<", "<=", ">", ">=")
            ):
                return expression
            self.advance()
            right = self.parse_term()
            expression = Binary(expression, operator.value, right, operator.location)

    def parse_term(self) -> Expression:
        expression = self.parse_factor()
        while True:
            operator = self.current_token()
            if (
                operator is None
                or operator.type != TokenType.OPERATOR
                or operator.value not in ("+", "-")
            ):
                return expression
            self.advance()
            right = self.parse_factor()
            expression = Binary(expression, operator.value, right, operator.location)

    def parse_factor(self) -> Expression:
        expression = self.parse_power()
        while True:
            operator = self.current_token()
            if (
                operator is None
                or operator.type != TokenType.OPERATOR
                or operator.value not in ("*", "/", "%")
            ):
                return expression
            self.advance()
            right = self.parse_power()
            expression = Binary(expression, operator.value, right, operator.location)

    def parse_power(self) -> Expression:
        expression = self.parse_unary()
        operator = self.match(TokenType.OPERATOR, "^")
        if operator is None:
            return expression

        right = self.parse_power()
        return Binary(expression, operator.value, right, operator.location)

    def parse_unary(self) -> Expression:
        operator = self.current_token()
        if (
            operator is not None
            and operator.type == TokenType.OPERATOR
            and operator.value in ("!", "+", "-")
        ):
            self.advance()
            return Unary(operator.value, self.parse_unary(), operator.location)

        return self.parse_primary()

    def parse_primary(self) -> Expression:
        token = self.current_token()
        if token is None:
            raise ParserError("Expected an expression, but reached the end of the input")

        if self.match(TokenType.L_PAREN) is not None:
            expression = self.parse_expression()
            self.expect(TokenType.R_PAREN)
            return expression

        if token.type == TokenType.NUMBER:
            self.advance()
            return Literal(token.value, "number", token.location)

        if token.type == TokenType.STRING:
            self.advance()
            return Literal(token.value, "string", token.location)

        if token.type == TokenType.KEYWORD and token.value in ("true", "false"):
            self.advance()
            return Literal(token.value, "bool", token.location)

        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(token.value, token.location)

        raise ParserError(
            f"Expected a name or literal, found {token.value!r} "
            f"at {token.location}"
        )
