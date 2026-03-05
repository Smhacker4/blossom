from .tokens import TT, Token, KEYWORDS
from .errors import BlossomLexError


class Lexer:
    def __init__(self, source: str):
        self.source = source

    def tokenize(self) -> list:
        tokens = []
        indent_stack = [0]
        lines = self.source.split('\n')

        for line_num, line in enumerate(lines, 1):
            stripped = line.lstrip()

            # Skip blank lines and comment-only lines
            if not stripped or stripped.startswith('#'):
                continue

            indent = len(line) - len(stripped)
            current = indent_stack[-1]

            if indent > current:
                indent_stack.append(indent)
                tokens.append(Token(TT.INDENT, indent, line_num))
            elif indent < current:
                while indent_stack[-1] > indent:
                    indent_stack.pop()
                    tokens.append(Token(TT.DEDENT, indent, line_num))
                if indent_stack[-1] != indent:
                    raise BlossomLexError(
                        f"The indentation on line {line_num} doesn't match any earlier level. "
                        "Check that you're using the same number of spaces consistently.",
                        line_num
                    )

            line_tokens = self._tokenize_line(stripped, line_num)
            tokens.extend(line_tokens)
            tokens.append(Token(TT.NEWLINE, '\n', line_num))

        # Close remaining open blocks
        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token(TT.DEDENT, 0, len(lines)))

        tokens.append(Token(TT.EOF, None, len(lines)))
        return tokens

    def _tokenize_line(self, line: str, line_num: int) -> list:
        tokens = []
        i = 0

        while i < len(line):
            ch = line[i]

            if ch == ' ' or ch == '\t':
                i += 1
                continue

            if ch == '#':
                break

            # String literals
            if ch in ('"', "'"):
                quote = ch
                i += 1
                start = i
                value_chars = []
                while i < len(line) and line[i] != quote:
                    if line[i] == '\\' and i + 1 < len(line):
                        esc = line[i + 1]
                        if esc == 'n':
                            value_chars.append('\n')
                        elif esc == 't':
                            value_chars.append('\t')
                        elif esc == '\\':
                            value_chars.append('\\')
                        else:
                            value_chars.append(esc)
                        i += 2
                    else:
                        value_chars.append(line[i])
                        i += 1
                if i >= len(line):
                    raise BlossomLexError(
                        f"You opened a string with {quote} but never closed it. "
                        f"Every opening quote needs a matching closing quote.",
                        line_num
                    )
                tokens.append(Token(TT.STRING, ''.join(value_chars), line_num))
                i += 1
                continue

            # Numbers
            if ch.isdigit():
                start = i
                while i < len(line) and (line[i].isdigit() or line[i] == '.'):
                    i += 1
                num_str = line[start:i]
                try:
                    value = float(num_str) if '.' in num_str else int(num_str)
                except ValueError:
                    raise BlossomLexError(f"'{num_str}' is not a valid number.", line_num)
                tokens.append(Token(TT.NUMBER, value, line_num))
                continue

            # Identifiers and keywords
            if ch.isalpha() or ch == '_':
                start = i
                while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                word = line[start:i]
                lower = word.lower()
                tt = KEYWORDS.get(lower)
                if tt is not None:
                    tokens.append(Token(tt, lower, line_num))
                else:
                    tokens.append(Token(TT.NAME, word, line_num))
                continue

            # Operators and punctuation
            simple = {
                '+': TT.PLUS, '-': TT.MINUS, '*': TT.STAR,
                '/': TT.SLASH, '%': TT.PERCENT, ':': TT.COLON,
                ',': TT.COMMA, '(': TT.LPAREN, ')': TT.RPAREN,
            }
            if ch in simple:
                tokens.append(Token(simple[ch], ch, line_num))
                i += 1
                continue

            raise BlossomLexError(
                f"I don't understand the character '{ch}'. "
                "Check for typos or unsupported symbols.",
                line_num
            )

        return tokens
