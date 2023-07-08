from lexer import Lexer
from parser import Parser
from evaluator import eval


print("Welcome to the vih REPL!")
try:
    while True:
        print(">> ", end='')
        input_string = input()
        lex = Lexer(input_string)
        parser = Parser(lex)
        program = parser.parse_program()
        result = eval(program)

        if parser.errors:
            print('\n'.join(parser.errors))
            continue
        if result is not None:
            print(result)
except KeyboardInterrupt:
    print("\nBye!")
