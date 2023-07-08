from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Optional, List

from lexer import Lexer, Token, TokenType


class Precedence(Enum):
    LOWEST = auto()
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    PREFIX = auto()
    CALL = auto()

    def __lt__(self, other):
        return self.value < other.value


PRECEDENCES = {
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.DIV: Precedence.PRODUCT,
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NEQ: Precedence.EQUALS,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.LEQ: Precedence.LESSGREATER,
    TokenType.GEQ: Precedence.LESSGREATER,
    TokenType.LPAR: Precedence.CALL,
}


class Node(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def __str__(self):
        pass


class Statement(Node):
    def __init__(self, token):
        self.token = token


class Expression(Node):
    def __init__(self, token):
        self.token = token


class Program(Node):
    def __init__(self, token):
        self.token = token
        self.statements = []

    def __str__(self):
        return ' '.join([str(stmt) for stmt in self.statements])


class ExpressionStatement(Statement):
    def __init__(self, token):
        super().__init__(token)
        # TODO: supply nodes with everything on creation?
        self.expression: Optional[Expression] = None

    def __str__(self):
        return f"{self.expression};"


class LetStatement(Statement):
    def __init__(self, token):
        super().__init__(token)
        self.name: Optional[Identifier] = None
        self.value: Optional[Expression] = None

    def __str__(self):
        return f"{self.token.literal} {self.name} = {self.value};"


class ReturnStatement(Statement):
    def __init__(self, token):
        super().__init__(token)
        self.return_value: Optional[Expression] = None

    def __str__(self):
        return f"{self.token.literal} {self.return_value};"


class BlockStatement(Statement):
    def __init__(self, token):
        super().__init__(token)
        self.statements: List[Statement] = []

    def __str__(self):
        return f"{' '.join([str(stmt) for stmt in self.statements])}"


class Identifier(Expression):
    def __init__(self, token, value):
        super().__init__(token)
        self.value: str = value

    def __str__(self):
        return f"{self.value}"


class IntegerLiteral(Expression):
    def __init__(self, token, value):
        super().__init__(token)
        self.value: int = value

    def __str__(self):
        return f"{self.value}"


class FunctionLiteral(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.parameters: List[Identifier] = []
        self.body: Optional[BlockStatement] = None

    def __str__(self):
        params = ', '.join([str(p) for p in self.parameters])
        return f"func({params}) {self.body}"


class Boolean(Expression):
    def __init__(self, token, value):
        super().__init__(token)
        self.value: bool = value

    def __str__(self):
        return f"{self.value}"


class PrefixExpression(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.operator: str = ''
        self.right: Optional[Expression] = None

    def __str__(self):
        return f"({self.operator}{self.right})"


class InfixExpression(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.left: Optional[Expression] = None
        self.operator: str = ''
        self.right: Optional[Expression] = None

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


class IfExpression(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.condition: Optional[Expression] = None
        self.consequence: Optional[BlockStatement] = None
        self.alternative: Optional[BlockStatement] = None

    def __str__(self):
        if self.alternative is not None:
            return f"if ({self.condition}) {{{self.consequence}}} else {{{self.alternative}}}"
        return f"if ({self.condition}) {{{self.consequence}}}"


class CallExpression(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.function: Optional[Expression] = None
        self.arguments: List[Expression] = []

    def __str__(self):
        args = ', '.join([str(a) for a in self.arguments])
        return f"{self.function}({args})"


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
            TokenType.FUNC: self.parse_function_literal,
            TokenType.TRUE: self.parse_boolean,
            TokenType.FALSE: self.parse_boolean,
            TokenType.NOT: self.parse_prefix_expression,
            TokenType.MINUS: self.parse_prefix_expression,
            TokenType.LPAR: self.parse_grouped_expression,
            TokenType.IF: self.parse_if_expression,
        }
        self.infix_functions = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.ASTERISK: self.parse_infix_expression,
            TokenType.DIV: self.parse_infix_expression,
            TokenType.LT: self.parse_infix_expression,
            TokenType.GT: self.parse_infix_expression,
            TokenType.EQ: self.parse_infix_expression,
            TokenType.NEQ: self.parse_infix_expression,
            TokenType.LEQ: self.parse_infix_expression,
            TokenType.GEQ: self.parse_infix_expression,
            TokenType.LPAR: self.parse_call_expression,
        }

    def parse_program(self) -> Program:
        self.program = Program(self.cur_token)
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
        self.advance_tokens()
        stmt.value = self.parse_expression(Precedence.LOWEST)
        if self._peek_token_is(TokenType.SEMICOLON):
            self.advance_tokens()
        return stmt

    def parse_return_statement(self):
        stmt = ReturnStatement(self.cur_token)
        self.advance_tokens()

        stmt.return_value = self.parse_expression(Precedence.LOWEST)
        if self._peek_token_is(TokenType.SEMICOLON):
            self.advance_tokens()
        return stmt

    def parse_block_statement(self) -> BlockStatement:
        if not self._cur_token_is(TokenType.LCURLY):
            self.errors.append("Expected '{' at the beginning of a block statement.")
        self.advance_tokens()
        block_stmt = BlockStatement(self.cur_token)
        while not self._cur_token_is(TokenType.RCURLY):
            stmt = self.parse_statement()
            if stmt is not None:
                block_stmt.statements.append(stmt)
            self.advance_tokens()
        if self._peek_token_is(TokenType.SEMICOLON):
            self.advance_tokens()
        return block_stmt

    def parse_expression_statement(self):
        stmt = ExpressionStatement(self.cur_token)
        stmt.expression = self.parse_expression(Precedence.LOWEST)
        if self._peek_token_is(TokenType.SEMICOLON):
            self.advance_tokens()
        return stmt

    def parse_expression(self, precedence: Precedence):
        prefix = self.prefix_functions.get(self.cur_token.token_type, None)
        if prefix is None:
            self.errors.append(f"No prefix parser function for {self.cur_token}")
            return None
        left_exp = prefix()

        while not self._peek_token_is(TokenType.SEMICOLON) and precedence < self._peek_precedence():
            infix = self.infix_functions.get(self.next_token.token_type, None)
            if infix is None:
                return left_exp
            self.advance_tokens()
            left_exp = infix(left_exp)
        return left_exp

    def parse_prefix_expression(self):
        expr = PrefixExpression(self.cur_token)
        expr.operator = self.cur_token.literal
        self.advance_tokens()
        expr.right = self.parse_expression(Precedence.PREFIX)
        return expr

    def parse_infix_expression(self, left_expr: Expression):
        expr = InfixExpression(self.cur_token)
        expr.left = left_expr
        expr.operator = self.cur_token.literal
        precedence = self._cur_precedence()
        self.advance_tokens()
        expr.right = self.parse_expression(precedence)
        return expr

    def parse_grouped_expression(self):
        self.advance_tokens()
        expr = self.parse_expression(Precedence.LOWEST)
        if not self._expect_peek(TokenType.RPAR):
            return None
        return expr

    def parse_if_expression(self):
        expr = IfExpression(self.cur_token)
        if not self._expect_peek(TokenType.LPAR):
            return None
        self.advance_tokens()
        expr.condition = self.parse_expression(Precedence.LOWEST)
        if not self._expect_peek(TokenType.RPAR):
            return None
        self.advance_tokens()
        expr.consequence = self.parse_block_statement()
        if self._peek_token_is(TokenType.ELSE):
            self.advance_tokens()
            self.advance_tokens()
            expr.alternative = self.parse_block_statement()
        return expr

    def parse_call_expression(self, function):
        expr = CallExpression(self.cur_token)
        expr.function = function
        expr.arguments = self.parse_call_arguments()
        return expr

    def parse_call_arguments(self):
        args = []
        if self._peek_token_is(TokenType.RPAR):
            self.advance_tokens()
            return args
        self.advance_tokens() 
        args.append(self.parse_expression(Precedence.LOWEST))
        
        while self._peek_token_is(TokenType.COMMA):
            self.advance_tokens()
            self.advance_tokens()
            args.append(self.parse_expression(Precedence.LOWEST))

        if not self._expect_peek(TokenType.RPAR):
            return None
        return args

    def parse_identifier(self):
        return Identifier(self.cur_token, self.cur_token.literal)

    def parse_integer_literal(self):
        return IntegerLiteral(self.cur_token, int(self.cur_token.literal))

    def parse_function_literal(self):
        expr = FunctionLiteral(self.cur_token)
        if not self._expect_peek(TokenType.LPAR):
            return None

        expr.parameters = self.parse_function_parameters()

        if not self._expect_peek(TokenType.LCURLY):
            return None
        expr.body = self.parse_block_statement()
        return expr

    def parse_function_parameters(self):
        params = []
        if self._peek_token_is(TokenType.RPAR):
            self.advance_tokens()
            return params

        self.advance_tokens()
        params.append(self.parse_identifier())

        while self._peek_token_is(TokenType.COMMA):
            self.advance_tokens()
            self.advance_tokens()
            params.append(self.parse_identifier())

        if not self._expect_peek(TokenType.RPAR):
            return None
        return params

    def parse_boolean(self):
        value = True if self.cur_token.literal == 'true' else False
        return Boolean(self.cur_token, value)

    def advance_tokens(self) -> None:
        self.cur_token = self.next_token
        self.next_token = self.lexer.next_token()

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

    def _cur_precedence(self):
        precedence = PRECEDENCES.get(self.cur_token.token_type, None)
        if precedence is not None:
            return precedence
        return Precedence.LOWEST

    def _peek_precedence(self):
        precedence = PRECEDENCES.get(self.next_token.token_type, None)
        if precedence is not None:
            return precedence
        return Precedence.LOWEST

