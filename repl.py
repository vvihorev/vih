from lexer import Lexer
from parser import Parser


print("Welcome to the vih REPL!")
try:
    while True:
        print(">> ", end='')
        input_string = input()
        lex = Lexer(input_string)
        parser = Parser(lex)
        program = parser.parse_program()

        if parser.errors:
            print('\n'.join(parser.errors))
            continue
        print(program)
except KeyboardInterrupt:
    print("\nBye!")
