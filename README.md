# 🌸 Blossom

**A beginner-friendly programming language that reads like plain English.**

Blossom is built for first-time programmers.
Under the hood it is a real language implementation in Python: lexer, parser, AST, and interpreter.

```blossom
say "Hello, world!"
ask "What is your name? " and store in name
say "Nice to meet you, " + name + "!"
```

## Why Blossom

Programming can feel hostile at the start. Blossom is designed to reduce that friction.

- Readable English-style syntax
- Friendly, actionable errors
- Simple, focused feature set
- No setup-heavy imports for beginner exercises

## Features

- `say` output and `ask` input
- Variables and arithmetic
- Conditions with natural comparison words
- Loops: `repeat ... times`, `repeat while`, `for each`
- Lists: create, add, remove, index, contains, length
- Functions: `define`, `call`, `give back`
- Built-ins: random numbers, type conversion

## Quick Start

### Requirements

- Python 3.8+

### Run from source

```bash
git clone https://github.com/Smhacker4/blossom.git
cd blossom
python blossom.py run examples/hello_world.bls
```

### Start REPL

```bash
python blossom.py
```

## Language Tour

### Output and Variables

```blossom
say "Hello, World!"
set age to 16
say "Age: " + age
```

### Input

```blossom
ask "What is your name? " and store in name
say "Hello, " + name + "!"
```

### Conditions

```blossom
if age is greater than 18:
    say "Adult"
otherwise if age is 18:
    say "Just turned 18"
otherwise:
    say "Minor"
```

Comparison forms:

- `is`
- `is not`
- `is greater than`
- `is less than`
- `is at least`
- `is at most`
- `contains`

### Loops

```blossom
repeat 3 times:
    say "Hi"

set i to 1
repeat while i is at most 3:
    say i
    set i to i + 1
```

### Lists

```blossom
make a list called fruits with "apple", "banana"
add "mango" to fruits
say fruits at 1
say length of fruits
if fruits contains "banana":
    say "Found banana"
remove "banana" from fruits
```

### Functions

```blossom
define add with a, b:
    give back a + b

set result to call add with 10, 25
say result
```

## Example Programs

- `examples/hello_world.bls`
- `examples/fizzbuzz.bls`
- `examples/lists.bls`
- `examples/functions.bls`
- `examples/guessing_game.bls`

Run an example:

```bash
python blossom.py run examples/fizzbuzz.bls
```

## Project Structure

```text
blossom/
|-- blossom.py                # CLI entry point
|-- README.md
|-- blossom/
|   |-- __init__.py           # Public API
|   |-- tokens.py             # Token types + keywords
|   |-- lexer.py              # Source -> tokens
|   |-- ast_nodes.py          # AST node definitions
|   |-- parser.py             # Tokens -> AST
|   |-- interpreter.py        # AST execution
|   |-- errors.py             # Friendly error classes
|   `-- repl.py               # Interactive shell
`-- examples/                 # Sample Blossom programs
```

## Error Style

Blossom errors are meant to guide beginners:

```text
Blossom Error on line 3:
I don't know what 'scroe' is. Did you forget to create it with 'set' first?
```

## Current Limits

- No modules/import system yet
- No file I/O yet
- Limited standard library

## Roadmap

- String interpolation (`"Hello, {name}!"`)
- More built-in functions (math/string helpers)
- File read/write syntax
- VS Code syntax highlighting
- Browser playground

## Contributing

Issues and pull requests are welcome.

To add language features, usually update in this order:

1. `blossom/tokens.py`
2. `blossom/lexer.py`
3. `blossom/parser.py`
4. `blossom/interpreter.py`

## License

MIT
