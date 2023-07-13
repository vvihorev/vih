import sys

from src.lexer import Lexer, TokenType
from src.parser import Parser
from src.evaluator import eval, Environment


option = None
if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: python3 vih.py <input_file> [lexer|parser|eval]")
    exit()
elif len(sys.argv) == 3:
    file, option = sys.argv[1], sys.argv[2]
else:
    file = sys.argv[1]

trace_eval = False
trace_parsing = False
match option:
    case 'lexer':
        with open(file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            lex = Lexer(line)
            token = lex.next_token()
            while token.token_type != TokenType.EOF:
                print(token, end=' ')
                token = lex.next_token()
            print()
        exit()
    case 'parser':
        trace_parsing = True
    case 'eval':
        trace_eval = True
    case None:
        pass
    case _:
        print('unknown option %s, use: "lexer", "parser", "eval"' % option)
        exit()


with open(file, 'r') as f:
    input_string = f.read()

env = Environment(trace_eval=trace_eval)
lex = Lexer(input_string)
parser = Parser(lex, trace_parsing=trace_parsing)
program = parser.parse_program()
result = eval(program, env)

if parser.errors:
    print('\n'.join(parser.errors))
    exit()
if result is not None:
    print(result)
