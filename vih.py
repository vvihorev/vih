import sys

from lexer import Lexer
from parser import Parser
from evaluator import eval, Environment


if len(sys.argv) != 2:
    print("Usage: python3 vih.py <input_file>")
    exit()

with open(sys.argv[1], 'r') as f:
    input_string = f.read()
    input_string = input_string.replace('\n', '')

env = Environment()
lex = Lexer(input_string)
parser = Parser(lex)
program = parser.parse_program()
result = eval(program, env)

if parser.errors:
    print('\n'.join(parser.errors))
    exit()
if result is not None:
    print(result)
