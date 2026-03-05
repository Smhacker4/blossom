from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .errors import BlossomError

BANNER = """
  ____  _
 | __ )| | ___  ___ ___  ___  _ __ ___
 |  _ \\| |/ _ \\/ __/ __|/ _ \\| '_ ` _ \\
 | |_) | | (_) \\__ \\__ \\ (_) | | | | | |
 |____/|_|\\___/|___/___/\\___/|_| |_| |_|

  A friendly programming language for everyone.
  Type 'quit' to exit.  Type 'help' for examples.
"""

HELP_TEXT = """
  Basic examples:
    say "Hello, World!"
    set name to "Alice"
    say "Hello, " + name + "!"
    if name is "Alice":
        say "Hi Alice!"
    set score to random number between 1 and 100
    say score

  Type your code line by line, or run a file:
    blossom run myfile.bls
"""


def run_repl():
    print(BANNER)
    interpreter = Interpreter()
    buffer = []
    indent_level = 0

    while True:
        prompt = '... ' if indent_level > 0 else '>>> '
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print('\nGoodbye!')
            break

        if line.strip() == 'quit':
            print('Goodbye!')
            break

        if line.strip() == 'help':
            print(HELP_TEXT)
            continue

        buffer.append(line)

        # Track indentation to know when a block is complete
        stripped = line.strip()
        if stripped.endswith(':'):
            indent_level += 1
            continue

        if stripped == '' and indent_level > 0:
            indent_level -= 1
            if indent_level > 0:
                continue

        if indent_level > 0:
            continue

        # Execute the buffered code
        source = '\n'.join(buffer)
        buffer = []
        indent_level = 0

        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            program = parser.parse()
            interpreter.run(program)
        except BlossomError as e:
            print(str(e))
        except Exception as e:
            print(f"\n  Internal error: {e}\n")
