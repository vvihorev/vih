from typing import Optional
from enum import Enum, auto


class TokenType(Enum):
    # Characters
    ILLEGAL = auto()
    LPAR = auto()
    RPAR = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    MINUS = auto()
    PLUS = auto()
    ASTERISK = auto()
    DIV = auto()
    EQUALS = auto()

    # Special words and identifiers
    IF = auto()
    ELSE = auto()
    FOR = auto()
    FUNC = auto()
    LET = auto()

    ID = auto()
    DIGIT = auto()


KEYWORDS = {
    'if': TokenType.IF,    
    'else': TokenType.ELSE,    
    'for': TokenType.FOR,    
    'func': TokenType.FUNC,    
    'let': TokenType.LET,
}


class Token:
    def __init__(self, token_type: TokenType, literal: str):
        self.token_type = token_type
        self.literal = literal

    def __str__(self):
        return f"{{{self.token_type}:'{self.literal}'}}"


class Lexer:
    def __init__(self, input_string: str):
        self.input_string = input_string
        self.position = 0
        self.ch = ''

    def next_token(self) -> Optional[Token]:
        if self.position >= len(self.input_string):
            return None
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
                token = Token(TokenType.DIV, self.ch)
            case '=':
                token = Token(TokenType.EQUALS, self.ch)
            # Trailing whitespace in file
            case ' ':
                return None
            case ch:
                if ch.isdigit():
                    token = Token(TokenType.DIGIT, self._match_digit())
                elif ch.isalpha() or ch == '_':
                    token = self._get_identifier()
                else:
                    # TODO: handle errors?
                    token = Token(TokenType.ILLEGAL, self.ch)
        self.position += 1
        return token

    def _skip_whitespace(self) -> None:
        while self.ch.isspace() and self.position < len(self.input_string):
            self._advance()

    def _match_digit(self) -> str:
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

        identifier = ''.join(identifier)
        keyword_token = self._get_keyword_identifier(identifier)
        self.position -= 1
        if keyword_token is not None:
            return keyword_token
        return Token(TokenType.ID, identifier)

    def _get_keyword_identifier(self, identifier: str) -> Optional[Token]:
        if identifier in KEYWORDS:
            return Token(KEYWORDS[identifier], identifier)
        return None

    def _advance(self):
        self.position += 1
        if self.position < len(self.input_string):
            self.ch = self.input_string[self.position]

