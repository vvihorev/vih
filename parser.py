from enum import Enum, auto
from abc import ABC#, abstractmethod
from typing import Optional

from lexer import Lexer, Token, TokenType


class Precedence(Enum):
    LOWEST = auto()
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    PREFIX = auto()
    CALL = auto()


class Node(ABC):
    def __init__(self):
        self.token_literal: str

    def __str__(self):
        pass


class Statement(Node):
    def __init__(self, token):
        self.token = token
        super().__init__()


class Expression(Node):
    def __init__(self):
        super().__init__()



class Program(Node):
    def __init__(self):
        super().__init__()
        self.statements = []

    def __str__(self):
        return ' '.join([str(stmt) for stmt in self.statements])


class ExpressionStatement(Statement):
    def __init__(self, token):
        super().__init__(token)
        self.expression: Expression = None

    def __str__(self):
        return f"{self.expression};"


class LetStatement(Statement):
    def __init__(self, token):
        super().__init__(token)
        self.name: Identifier = None
        self.value: Expression = None

    def __str__(self):
        return f"{self.token.literal} {self.name} = {self.value};"


class ReturnStatement(Statement):
    def __init__(self, token):
        super().__init__(token)
        self.return_value: Expression = None

    def __str__(self):
        return f"{self.token.literal} {self.return_value};"


class Identifier(Expression):
    def __init__(self, token, value):
        super().__init__()
        self.token: Token = token
        self.value: str = value

    def __str__(self):
        return f"{self.value}"


class IntegerLiteral(Expression):
    def __init__(self, token, value):
        super().__init__()
        self.token: Token = token
        self.value: int = value

    def __str__(self):
        return f"{self.value}"


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer: Lexer = lexer
        self.cur_token: Token = self.lexer.next_token()
        self.next_token: Token = self.lexer.next_token()

        self.errors = []
        self.program = None
        
        self.prefix_functions = {
            TokenType.ID: self.parse_identifier,
            TokenType.DIGIT: self.parse_integer_literal,
        }
        self.infix_functions = {}

    def advance_tokens(self) -> None:
        self.cur_token = self.next_token
        self.next_token = self.lexer.next_token()

    def parse_program(self) -> Program:
        self.program = Program()
        self.program.token_literal = self.cur_token.literal
        while not self._cur_token_is(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                self.program.statements.append(stmt)
            self.advance_tokens()
        return self.program

    def parse_statement(self):
        match self.cur_token.token_type:
            case TokenType.LET:
                stmt = self.parse_let_statement()
            case TokenType.RETURN:
                stmt = self.parse_return_statement()
            case _:
                stmt = self.parse_expression_statement()
        return stmt

    def parse_let_statement(self) -> Optional[LetStatement]:
        stmt = LetStatement(self.cur_token)
        if not self._expect_peek(TokenType.ID):
            return None
        name = self.parse_identifier()
        stmt.name = name
        if not self._expect_peek(TokenType.EQUALS):
            return None
        # TODO: parse expression
        while not self._cur_token_is(TokenType.SEMICOLON) or self._cur_token_is(TokenType.EOF):
            self.advance_tokens()
        return stmt

    def parse_return_statement(self):
        stmt = ReturnStatement(self.cur_token)
        self.advance_tokens()

        while not self._cur_token_is(TokenType.SEMICOLON) or self._cur_token_is(TokenType.EOF):
            self.advance_tokens()
        return stmt

    def parse_expression_statement(self):
        stmt = ExpressionStatement(self.cur_token)
        # stmt.expression = self.parse_expression(Precedence.LOWEST)
        if self._peek_token_is(TokenType.SEMICOLON):
            self.advance_tokens()
        return stmt

    def parse_expression(self, precedence: Precedence):
        prefix = self.prefix_functions[self.cur_token.token_type]
        if not prefix:
            return None
        left_exp = prefix()

        return left_exp

    def parse_prefix_function(self):
        pass

    def parse_infix_function(self, expr: Expression):
        pass

    def parse_identifier(self):
        return Identifier(self.cur_token, self.cur_token.literal)

    def parse_integer_literal(self):
        return IntegerLiteral(self.cur_token, int(self.cur_token.literal))

    def _cur_token_is(self, tt: TokenType):
        return self.cur_token.token_type == tt

    def _peek_token_is(self, tt: TokenType):
        return self.next_token.token_type == tt

    def _expect_peek(self, tt: TokenType):
        if self._peek_token_is(tt):
            self.advance_tokens()
            return True
        else:
            self._peek_error(tt)
            return False

    def _peek_error(self, tt):
        self.errors.append(f"Expected next token to be {tt}, got {self.next_token.token_type}.")


if __name__ == "__main__":
    lex = Lexer("let a = 4;let b = 5;")
    # lex = Lexer("-5;")
    parser = Parser(lex)

    parser.parse_program()
    if parser.errors:
        print(parser.errors)
    print(parser.program)
