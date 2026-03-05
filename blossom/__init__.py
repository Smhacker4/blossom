from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .errors import BlossomError, BlossomLexError, BlossomParseError, BlossomRuntimeError


def run_source(source: str):
    """Lex, parse, and interpret a Blossom source string."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    interpreter = Interpreter()
    interpreter.run(program)
