from enum import Enum, auto


class TokenType(Enum):
    # Characters
    EOF = auto()
    COMMENT = auto()
    ILLEGAL = auto()
    LPAR = auto()
    RPAR = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LCURLY = auto()
    RCURLY = auto()
    SEMICOLON = auto()
    COMMA = auto()
    STRING = auto()

    EQUALS = auto()
    MINUS = auto()
    PLUS = auto()
    ASTERISK = auto()
    DIV = auto()

    # Comparison operators
    GT = auto()
    LT = auto()
    GEQ = auto()
    LEQ = auto()
    EQ = auto()
    NEQ = auto()

    # Logical operators
    NOT = auto()
    TRUE = auto()
    FALSE = auto()

    # Special words and identifiers
    IF = auto()
    ELSE = auto()
    FOR = auto()
    FUNC = auto()
    LET = auto()
    RETURN = auto()

    ID = auto()
    DIGIT = auto()


KEYWORDS = {
    'if': TokenType.IF,    
    'else': TokenType.ELSE,    
    'for': TokenType.FOR,    
    'func': TokenType.FUNC,    
    'let': TokenType.LET,
    'return': TokenType.RETURN,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
}


class Token:
    def __init__(self, token_type: TokenType, literal: str):
        self.token_type = token_type
        self.literal = literal

    def __str__(self):
        return f"{{{self.token_type.name}:'{self.literal}'}}"


class Lexer:
    def __init__(self, input_string: str):
        self.input_string = input_string
        self.position = 0
        self.ch = ''

    def next_token(self) -> Token:
        if self.position >= len(self.input_string):
            return Token(TokenType.EOF, '')
        self.ch = self.input_string[self.position]
        self._skip_whitespace()
        match self.ch:
            case '[':
                token = Token(TokenType.LBRACKET, self.ch)
            case ']':
                token = Token(TokenType.RBRACKET, self.ch)
            case '(':
                token = Token(TokenType.LPAR, self.ch)
            case ')':
                token = Token(TokenType.RPAR, self.ch)
            case '{':
                token = Token(TokenType.LCURLY, self.ch)
            case '}':
                token = Token(TokenType.RCURLY, self.ch)
            case ';':
                token = Token(TokenType.SEMICOLON, self.ch)
            case ',':
                token = Token(TokenType.COMMA, self.ch)
            case '-':
                token = Token(TokenType.MINUS, self.ch)
            case '+':
                token = Token(TokenType.PLUS, self.ch)
            case '*':
                token = Token(TokenType.ASTERISK, self.ch)
            case '/':
                if self._peek() == '/':
                    comment = []
                    while self.ch != '\n' and self.position < len(self.input_string):
                        comment.append(self.ch)
                        self._advance()
                    token = Token(TokenType.COMMENT, ''.join(comment))
                else:
                    token = Token(TokenType.DIV, self.ch)
            case '"':
                string_literal = []
                self._advance()
                while self.ch != '"' and self.position < len(self.input_string):
                    string_literal.append(self.ch)
                    self._advance()
                token = Token(TokenType.STRING, ''.join(string_literal))
            case '=':
                if self._peek() == '=':
                    token = Token(TokenType.EQ, self.ch + '=')
                    self.position += 1
                else:
                    token = Token(TokenType.EQUALS, self.ch)
            case '!':
                if self._peek() == '=':
                    token = Token(TokenType.NEQ, self.ch + '=')
                    self.position += 1
                else:
                    token = Token(TokenType.NOT, self.ch)
            case '<':
                if self._peek() == '=':
                    token = Token(TokenType.LEQ, self.ch + '=')
                    self.position += 1
                else:
                    token = Token(TokenType.LT, self.ch)
            case '>':
                if self._peek() == '=':
                    token = Token(TokenType.GEQ, self.ch + '=')
                    self.position += 1
                else:
                    token = Token(TokenType.GT, self.ch)
            case '\n':
                self._advance()
                return self.next_token()
            case ' ':
                return Token(TokenType.EOF, '')
            case ch:
                if ch.isdigit():
                    token = Token(TokenType.DIGIT, self._get_digit())
                elif ch.isalpha() or ch == '_':
                    token = self._get_identifier()
                else:
                    token = Token(TokenType.ILLEGAL, self.ch)
        self.position += 1
        return token

    def _peek(self) -> str:
        if self.position < len(self.input_string) - 1:
            return self.input_string[self.position + 1]
        return ''

    def _advance(self):
        self.position += 1
        if self.position < len(self.input_string):
            self.ch = self.input_string[self.position]
        else:
            self.ch = ' '

    def _skip_whitespace(self) -> None:
        while self.ch.isspace() and self.position < len(self.input_string):
            self._advance()

    def _get_digit(self) -> str:
        digit = []
        while self.ch.isdigit() and self.position < len(self.input_string):
            digit.append(self.ch)
            self._advance()
        self.position -= 1
        return ''.join(digit)

    def _get_identifier(self) -> Token:
        identifier = []
        char_suitable = lambda ch: ch.isalnum() or ch == '_'
        while char_suitable(self.ch) and self.position < len(self.input_string):
            identifier.append(self.ch) 
            self._advance()
        self.position -= 1
        identifier = ''.join(identifier)
        if identifier in KEYWORDS:
            return Token(KEYWORDS[identifier], identifier)
        return Token(TokenType.ID, identifier)

