import pytest

from lexer import Lexer, TokenType, Token
from parser import Parser


def check_parser_errors(parser):
    if len(parser.errors) != 0:
        raise ValueError('\n'.join(parser.errors))


def test_pretty_printing():
    input_string = "let a = 3; return 45;"
    lex = Lexer(input_string)
    parser = Parser(lex)
    parser.parse_program()
    expected_output = "let a = None; return None;"
    assert str(parser.program) == expected_output


def test_let_statement():
    input = """
    let x = 5;
    let y = 10;
    let foobar = 838383;
    """
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()
    expected_ids = ['x', 'y', 'foobar']

    assert program is not None
    assert len(program.statements) == 3
    for stmt, id in zip(program.statements, expected_ids):
        assert stmt.token.token_type == TokenType.LET
        assert stmt.token.literal == 'let'
        assert stmt.name.value == id

    check_parser_errors(parser)


def test_return_statement():
    input = """
    return x;
    return 10;
    """
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert program is not None
    assert len(program.statements) == 2

    expected_tokens = [Token(TokenType.ID, 'x'), None]
    for stmt, token in zip(program.statements, expected_tokens):
        print(stmt)
        assert stmt.token.token_type == TokenType.RETURN
        if stmt.return_value:
            assert stmt.return_value.token == token
    check_parser_errors(parser)

