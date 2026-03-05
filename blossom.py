#!/usr/bin/env python3
"""
Blossom - A friendly programming language for everyone.

Usage:
  blossom.py run <file.bls>     Run a Blossom source file
  blossom.py                    Start the interactive REPL
"""

import sys
import os


def main():
    args = sys.argv[1:]

    if not args:
        from blossom.repl import run_repl
        run_repl()
        return

    if args[0] == 'run' and len(args) == 2:
        path = args[1]
        if not os.path.exists(path):
            print(f"\n  Blossom Error:\n  I can't find the file '{path}'. Check the filename and try again.\n")
            sys.exit(1)
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        _run(source, path)
        return

    print(__doc__)
    sys.exit(1)


def _run(source: str, filename: str = '<input>'):
    from blossom.lexer import Lexer
    from blossom.parser import Parser
    from blossom.interpreter import Interpreter
    from blossom.errors import BlossomError

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        interpreter = Interpreter()
        interpreter.run(program)
    except BlossomError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"\n  Internal error in {filename}: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
