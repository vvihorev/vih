from lexer import Lexer


print("Welcome to the vih REPL!")
try:
    while True:
        print(">> ", end='')
        input_string = input()
        lex = Lexer(input_string)
        token = lex.next_token()
        while token is not None:
            print(token)
            token = lex.next_token()
except KeyboardInterrupt:
    print("\nBye!")
