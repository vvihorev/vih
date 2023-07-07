from pytest import mark

from lexer import TokenType, Lexer


@mark.parametrize(
    'ch,tt', [
        ('(', TokenType.LPAR),
        (')', TokenType.RPAR),
        ('[', TokenType.LBRACKET),
        (']', TokenType.RBRACKET),
        (';', TokenType.SEMICOLON),
        (',', TokenType.COMMA),
        ('-', TokenType.MINUS),
        ('+', TokenType.PLUS),
        ('*', TokenType.ASTERISK),
        ('/', TokenType.DIV),
    ]
)
def test_valid_symbols(ch, tt):
    lex = Lexer(ch)
    token = lex.next_token()
    assert token is not None
    assert token.token_type == tt
    assert token.literal == ch
    assert lex.next_token() is None


@mark.parametrize(
    'ch,tt', [
        ('808723', TokenType.DIGIT),
        ('01', TokenType.DIGIT),
        ('2', TokenType.DIGIT),
        ('name', TokenType.ID),
        ('_name', TokenType.ID),
        ('na_me', TokenType.ID),
        ('name_', TokenType.ID),
        ('name_23', TokenType.ID),
        ('name_2', TokenType.ID),
    ]
)
def test_valid_digits_and_identifiers(ch, tt):
    lex = Lexer(ch)
    token = lex.next_token()
    assert token is not None
    assert token.token_type == tt
    assert token.literal == ch
    assert lex.next_token() is None


@mark.parametrize(
    'ch,tt', [
        ('for', TokenType.FOR),
        ('if', TokenType.IF),
        ('let', TokenType.LET),
        ('else', TokenType.ELSE),
        ('func', TokenType.FUNC),
    ]
)
def test_valid_keyword_identifiers(ch, tt):
    lex = Lexer(ch)
    token = lex.next_token()
    assert token is not None
    assert token.token_type == tt
    assert token.literal == ch
    assert lex.next_token() is None


@mark.parametrize(
    'cs,ts', [
        (
            'this for 2 (if a)', [
                (TokenType.ID, 'this'),
                (TokenType.FOR, 'for'),
                (TokenType.DIGIT, '2'),
                (TokenType.LPAR, '('),
                (TokenType.IF, 'if'),
                (TokenType.ID, 'a'),
                (TokenType.RPAR, ')'),
            ]
        ), (
            'aVar-23', [
                (TokenType.ID, 'aVar'),
                (TokenType.MINUS, '-'),
                (TokenType.DIGIT, '23'),
            ]
        ), (
            'x-y+3', [
                (TokenType.ID, 'x'),
                (TokenType.MINUS, '-'),
                (TokenType.ID, 'y'),
                (TokenType.PLUS, '+'),
                (TokenType.DIGIT, '3'),
            ]
        )
    ]
)
def test_valid_streams(cs, ts):
    lex = Lexer(cs)
    token = lex.next_token()
    cur_ts = 0
    while token is not None:
        assert token.token_type == ts[cur_ts][0]
        assert token.literal == ts[cur_ts][1]
        cur_ts += 1
        token = lex.next_token()


def test_trailing_whitespace():
    lex = Lexer("else   ")
    token = lex.next_token()
    assert token
    token = lex.next_token()


def test_comments():
   pass  
