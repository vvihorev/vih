from lexer import Lexer, TokenType


print("Welcome to the vih REPL!")
try:
    while True:
        print(">> ", end='')
        input_string = input()
        lex = Lexer(input_string)
        token = lex.next_token()
        while token.token_type != TokenType.EOF:
            print(token)
            token = lex.next_token()
except KeyboardInterrupt:
    print("\nBye!")
