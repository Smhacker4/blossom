from .tokens import TT, Token
from .ast_nodes import *
from .errors import BlossomParseError


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    # ── Token stream helpers ──────────────────────────────────────────────────

    def peek(self, offset=0) -> Token:
        i = self.pos + offset
        if i < len(self.tokens):
            return self.tokens[i]
        return self.tokens[-1]  # EOF

    def current(self) -> Token:
        return self.peek(0)

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def check(self, *types) -> bool:
        return self.current().type in types

    def match(self, *types) -> Optional[Token]:
        if self.check(*types):
            return self.advance()
        return None

    def consume(self, *types) -> Token:
        tok = self.current()
        if types and tok.type not in types:
            expected = ' or '.join(t.name for t in types)
            self._error(
                f"I expected {expected} here but found {tok.value!r} instead. "
                "Check for a typo or missing word.",
                tok.line
            )
        return self.advance()

    def skip_newlines(self):
        while self.check(TT.NEWLINE):
            self.advance()

    # Token types that can serve as identifiers (all word-like tokens)
    _NON_NAME_TYPES = {
        TT.NUMBER, TT.STRING,
        TT.COLON, TT.COMMA, TT.LPAREN, TT.RPAREN,
        TT.PLUS, TT.MINUS, TT.STAR, TT.SLASH, TT.PERCENT,
        TT.NEWLINE, TT.INDENT, TT.DEDENT, TT.EOF,
    }

    def consume_name(self) -> Token:
        """Accept any word token as a name (allows keywords as variable names)."""
        tok = self.current()
        if tok.type in self._NON_NAME_TYPES:
            self._error(
                f"I expected a name here but found {tok.value!r}. "
                "Names can be words like 'score', 'my_name', 'total', etc.",
                tok.line
            )
        return self.advance()



    def _error(self, msg, line=None):
        if line is None:
            line = self.current().line
        raise BlossomParseError(msg, line)

    # ── Top-level ─────────────────────────────────────────────────────────────

    def parse(self) -> Program:
        stmts = []
        self.skip_newlines()
        while not self.check(TT.EOF):
            stmt = self.parse_statement()
            stmts.append(stmt)
            self.skip_newlines()
        return Program(stmts)

    # ── Block ─────────────────────────────────────────────────────────────────

    def parse_block(self) -> list:
        """Here I'm just making it so that even if the user uses the colon, it can still be accepted"""
        if self.check(TT.COLON):
            self.consume(TT.COLON)
        elif self.check(TT.THEN):
            self.consume(TT.THEN)
        else:
            """
            I have no idea how to give errors the way you did yet, still insepecting
            If you want you can just add here: 
            'Expected a colon (:) or "then", maybe you forgot to add it to your if statment at line (line)'
            """
            return
        self.skip_newlines()
        self.consume(TT.INDENT)
        stmts = []
        self.skip_newlines()
        while not self.check(TT.DEDENT, TT.EOF):
            stmt = self.parse_statement()
            stmts.append(stmt)
            self.skip_newlines()
        if self.check(TT.DEDENT):
            self.advance()
        return stmts

    # ── Statements ────────────────────────────────────────────────────────────

    def parse_statement(self):
        tok = self.current()

        if tok.type == TT.SAY:
            return self.parse_say()
        if tok.type == TT.SET:
            return self.parse_set()
        if tok.type == TT.ASK:
            return self.parse_ask()
        if tok.type == TT.IF:
            return self.parse_if()
        if tok.type == TT.REPEAT:
            return self.parse_repeat()
        if tok.type == TT.MAKE:
            return self.parse_make_list()
        if tok.type == TT.ADD:
            return self.parse_add_to_list()
        if tok.type == TT.REMOVE:
            return self.parse_remove_from_list()
        if tok.type == TT.FOR:
            return self.parse_for_each()
        if tok.type == TT.DEFINE:
            return self.parse_define()
        if tok.type == TT.CALL:
            return self.parse_call_stmt()
        if tok.type == TT.GIVE:
            return self.parse_give_back()

        self._error(
            f"I don't know what to do with '{tok.value}' here. "
            "Each line should start with a Blossom keyword like 'say', 'set', 'if', etc.",
            tok.line
        )

    def parse_say(self):
        tok = self.consume(TT.SAY)
        expr = self.parse_expression()
        return SayStmt(expr, tok.line)

    def parse_set(self):
        tok = self.consume(TT.SET)
        name_tok = self.consume_name()
        self.consume(TT.TO)
        expr = self.parse_expression()
        return SetStmt(name_tok.value, expr, tok.line)

    def parse_ask(self):
        tok = self.consume(TT.ASK)
        prompt = self.parse_expression()
        self.consume(TT.AND)
        self.consume(TT.STORE)
        self.consume(TT.IN)
        name_tok = self.consume_name()
        return AskStmt(prompt, name_tok.value, tok.line)

    def parse_if(self):
        tok = self.consume(TT.IF)
        condition = self.parse_condition()
        body = self.parse_block()

        elseifs = []
        else_body = None

        self.skip_newlines()
        while self.check(TT.OTHERWISE):
            self.consume(TT.OTHERWISE)
            if self.check(TT.IF):
                self.consume(TT.IF)
                elif_cond = self.parse_condition()
                elif_body = self.parse_block()
                elseifs.append((elif_cond, elif_body))
                self.skip_newlines()
            else:
                else_body = self.parse_block()
                break

        return IfStmt(condition, body, elseifs, else_body, tok.line)

    def parse_repeat(self):
        tok = self.consume(TT.REPEAT)
        if self.check(TT.WHILE):
            self.consume(TT.WHILE)
            condition = self.parse_condition()
            body = self.parse_block()
            return RepeatWhileStmt(condition, body, tok.line)
        else:
            count = self.parse_expression()
            self.consume(TT.TIMES)
            body = self.parse_block()
            return RepeatTimesStmt(count, body, tok.line)

    def parse_make_list(self):
        tok = self.consume(TT.MAKE)
        self.consume(TT.A)
        self.consume(TT.LIST)
        self.consume(TT.CALLED)
        name_tok = self.consume_name()
        items = []
        if self.check(TT.WITH):
            self.consume(TT.WITH)
            items.append(self.parse_expression())
            while self.check(TT.COMMA):
                self.consume(TT.COMMA)
                items.append(self.parse_expression())
        return MakeListStmt(name_tok.value, items, tok.line)

    def parse_add_to_list(self):
        tok = self.consume(TT.ADD)
        expr = self.parse_expression()
        self.consume(TT.TO)
        name_tok = self.consume_name()
        return AddToListStmt(expr, name_tok.value, tok.line)

    def parse_remove_from_list(self):
        tok = self.consume(TT.REMOVE)
        expr = self.parse_expression()
        self.consume(TT.FROM)
        name_tok = self.consume_name()
        return RemoveFromListStmt(expr, name_tok.value, tok.line)

    def parse_for_each(self):
        tok = self.consume(TT.FOR)
        self.consume(TT.EACH)
        var_tok = self.consume_name()
        self.consume(TT.IN)
        list_tok = self.consume_name()
        body = self.parse_block()
        return ForEachStmt(var_tok.value, list_tok.value, body, tok.line)

    def parse_define(self):
        tok = self.consume(TT.DEFINE)
        name_tok = self.consume_name()
        params = []
        if self.check(TT.WITH):
            self.consume(TT.WITH)
            params.append(self.consume_name().value)
            while self.check(TT.COMMA):
                self.consume(TT.COMMA)
                params.append(self.consume_name().value)
        body = self.parse_block()
        return DefineStmt(name_tok.value, params, body, tok.line)

    def parse_call_stmt(self):
        tok = self.consume(TT.CALL)
        name_tok = self.consume_name()
        args = []
        if self.check(TT.WITH):
            self.consume(TT.WITH)
            args.append(self.parse_expression())
            while self.check(TT.COMMA):
                self.consume(TT.COMMA)
                args.append(self.parse_expression())
        return CallStmt(name_tok.value, args, tok.line)

    def parse_give_back(self):
        tok = self.consume(TT.GIVE)
        self.consume(TT.BACK)
        if self.check(TT.NOTHING):
            self.consume(TT.NOTHING)
            return GiveBackStmt(None, tok.line)
        expr = self.parse_expression()
        return GiveBackStmt(expr, tok.line)

    # ── Conditions ────────────────────────────────────────────────────────────

    def parse_condition(self):
        return self.parse_or_expr()

    def parse_or_expr(self):
        left = self.parse_and_expr()
        while self.check(TT.OR):
            self.consume(TT.OR)
            right = self.parse_and_expr()
            left = LogicalOp(left, 'or', right)
        return left

    def parse_and_expr(self):
        left = self.parse_comparison()
        while self.check(TT.AND):
            self.consume(TT.AND)
            right = self.parse_comparison()
            left = LogicalOp(left, 'and', right)
        return left

    def parse_comparison(self):
        if self.check(TT.NOT):
            tok = self.consume(TT.NOT)
            expr = self.parse_comparison()
            return NotExpr(expr, tok.line)

        left = self.parse_expression()

        if self.check(TT.IS):
            tok = self.consume(TT.IS)

            if self.check(TT.NOT):
                self.consume(TT.NOT)
                right = self.parse_expression()
                return Comparison(left, '!=', right, tok.line)

            if self.check(TT.GREATER):
                self.consume(TT.GREATER)
                self.consume(TT.THAN)
                right = self.parse_expression()
                return Comparison(left, '>', right, tok.line)

            if self.check(TT.LESS):
                self.consume(TT.LESS)
                self.consume(TT.THAN)
                right = self.parse_expression()
                return Comparison(left, '<', right, tok.line)

            if self.check(TT.AT):
                self.consume(TT.AT)
                if self.check(TT.LEAST):
                    self.consume(TT.LEAST)
                    right = self.parse_expression()
                    return Comparison(left, '>=', right, tok.line)
                if self.check(TT.MOST):
                    self.consume(TT.MOST)
                    right = self.parse_expression()
                    return Comparison(left, '<=', right, tok.line)
                self._error(
                    "After 'is at' I expected 'least' or 'most'. "
                    "Example: 'if score is at least 10:'",
                    tok.line
                )

            right = self.parse_expression()
            return Comparison(left, '==', right, tok.line)

        if self.check(TT.CONTAINS):
            tok = self.consume(TT.CONTAINS)
            right = self.parse_expression()
            return ContainsExpr(left, right, tok.line)

        return left

    # ── Expressions ───────────────────────────────────────────────────────────

    def parse_expression(self):
        return self.parse_term()

    def parse_term(self):
        left = self.parse_factor()
        while self.check(TT.PLUS, TT.MINUS):
            op_tok = self.advance()
            right = self.parse_factor()
            left = BinaryOp(left, op_tok.value, right, op_tok.line)
        return left

    def parse_factor(self):
        left = self.parse_unary()
        while self.check(TT.STAR, TT.SLASH, TT.PERCENT):
            op_tok = self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op_tok.value, right, op_tok.line)
        return left

    def parse_unary(self):
        if self.check(TT.MINUS):
            tok = self.consume(TT.MINUS)
            expr = self.parse_primary()
            return UnaryMinus(expr, tok.line)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()

        # Number literal
        if tok.type == TT.NUMBER:
            self.advance()
            return NumberLit(tok.value, tok.line)

        # String literal
        if tok.type == TT.STRING:
            self.advance()
            return StringLit(tok.value, tok.line)

        # Boolean literals
        if tok.type == TT.TRUE:
            self.advance()
            return BoolLit(True, tok.line)
        if tok.type == TT.FALSE:
            self.advance()
            return BoolLit(False, tok.line)

        # Nothing
        if tok.type == TT.NOTHING:
            self.advance()
            return NothingLit(tok.line)

        # Parenthesized expression
        if tok.type == TT.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.consume(TT.RPAREN)
            return expr

        # call expression (function call used as a value)
        if tok.type == TT.CALL:
            self.advance()
            name_tok = self.consume_name()
            args = []
            if self.check(TT.WITH):
                self.consume(TT.WITH)
                args.append(self.parse_expression())
                while self.check(TT.COMMA):
                    self.consume(TT.COMMA)
                    args.append(self.parse_expression())
            return CallExpr(name_tok.value, args, tok.line)

        # length of <name>
        if tok.type == TT.LENGTH:
            self.advance()
            self.consume(TT.OF)
            name_tok = self.consume_name()
            return LengthExpr(name_tok.value, tok.line)

        # random number between <expr> and <expr>
        if tok.type == TT.RANDOM:
            self.advance()
            self.consume(TT.NUMBER_KW)
            self.consume(TT.BETWEEN)
            low = self.parse_expression()
            self.consume(TT.AND)
            high = self.parse_expression()
            return RandomExpr(low, high, tok.line)

        # convert <expr> to number/text
        if tok.type == TT.CONVERT:
            self.advance()
            expr = self.parse_expression()
            self.consume(TT.TO)
            if self.check(TT.NUMBER_KW):
                self.advance()
                return ConvertExpr(expr, 'number', tok.line)
            if self.check(TT.TEXT):
                self.advance()
                return ConvertExpr(expr, 'text', tok.line)
            self._error(
                "After 'convert ... to' I expected 'number' or 'text'.",
                tok.line
            )

        # Identifier — may be followed by 'at <index>'
        if tok.type not in self._NON_NAME_TYPES:
            self.advance()
            if self.check(TT.AT):
                at_tok = self.consume(TT.AT)
                index = self.parse_expression()
                return IndexExpr(tok.value, index, at_tok.line)
            return Identifier(tok.value, tok.line)

        self._error(
            f"I expected a value here but found '{tok.value}'. "
            "Values can be numbers, text in quotes, true/false, or variable names.",
            tok.line
        )
