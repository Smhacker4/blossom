import random as _random
from .ast_nodes import *
from .errors import BlossomRuntimeError


class ReturnSignal(Exception):
    """Raised when 'give back' is executed inside a function."""
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name: str, line=None):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name, line)
        raise BlossomRuntimeError(
            f"I don't know what '{name}' is. "
            "Did you forget to create it with 'set' first?",
            line
        )

    def set(self, name: str, value):
        """Update variable if it exists anywhere in the chain; else create locally."""
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent and self.parent.has(name):
            self.parent.set(name, value)
            return
        self.vars[name] = value

    def define(self, name: str, value):
        """Always create in the current (local) scope — used for function params."""
        self.vars[name] = value

    def has(self, name: str) -> bool:
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.functions = {}  # name -> DefineStmt

    # ── Public entry point ────────────────────────────────────────────────────

    def run(self, program: Program):
        self._exec_stmts(program.stmts, self.global_env)

    # ── Statement execution ───────────────────────────────────────────────────

    def _exec_stmts(self, stmts: list, env: Environment):
        for stmt in stmts:
            self._exec(stmt, env)

    def _exec(self, node, env: Environment):
        t = type(node)

        if t == SayStmt:
            value = self._eval(node.expr, env)
            print(self._to_display(value))

        elif t == SetStmt:
            value = self._eval(node.expr, env)
            env.set(node.name, value)

        elif t == AskStmt:
            prompt = self._eval(node.prompt, env)
            try:
                answer = input(self._to_str(prompt))
            except EOFError:
                answer = ''
            env.set(node.var_name, answer)

        elif t == IfStmt:
            if self._eval(node.condition, env):
                self._exec_stmts(node.body, env)
            else:
                matched = False
                for elif_cond, elif_body in node.elseifs:
                    if self._eval(elif_cond, env):
                        self._exec_stmts(elif_body, env)
                        matched = True
                        break
                if not matched and node.else_body is not None:
                    self._exec_stmts(node.else_body, env)

        elif t == RepeatTimesStmt:
            count = self._eval(node.count, env)
            if not isinstance(count, (int, float)):
                raise BlossomRuntimeError(
                    f"'repeat ... times' needs a number, but I got {self._to_display(count)!r}.",
                    node.line
                )
            for _ in range(int(count)):
                self._exec_stmts(node.body, env)

        elif t == RepeatWhileStmt:
            limit = 100_000
            count = 0
            while self._eval(node.condition, env):
                self._exec_stmts(node.body, env)
                count += 1
                if count > limit:
                    raise BlossomRuntimeError(
                        "Your 'repeat while' loop has run more than 100,000 times. "
                        "It might be stuck. Check that the condition eventually becomes false.",
                        node.line
                    )

        elif t == MakeListStmt:
            items = [self._eval(i, env) for i in node.items]
            env.set(node.name, items)

        elif t == AddToListStmt:
            lst = self._get_list(node.list_name, env, node.line)
            value = self._eval(node.expr, env)
            lst.append(value)

        elif t == RemoveFromListStmt:
            lst = self._get_list(node.list_name, env, node.line)
            value = self._eval(node.expr, env)
            if value not in lst:
                raise BlossomRuntimeError(
                    f"{self._to_display(value)!r} is not in the list '{node.list_name}'.",
                    node.line
                )
            lst.remove(value)

        elif t == ForEachStmt:
            lst = self._get_list(node.list_name, env, node.line)
            for item in list(lst):  # copy so mutations during loop are safe
                env.set(node.var, item)
                self._exec_stmts(node.body, env)

        elif t == DefineStmt:
            self.functions[node.name] = node

        elif t == CallStmt:
            args = [self._eval(a, env) for a in node.args]
            self._call_function(node.name, args, env, node.line)

        elif t == GiveBackStmt:
            value = self._eval(node.expr, env) if node.expr is not None else None
            raise ReturnSignal(value)

        else:
            raise BlossomRuntimeError(f"Unknown statement type: {type(node).__name__}")

    # ── Expression evaluation ─────────────────────────────────────────────────

    def _eval(self, node, env: Environment):
        t = type(node)

        if t == NumberLit:
            return node.value

        if t == StringLit:
            return node.value

        if t == BoolLit:
            return node.value

        if t == NothingLit:
            return None

        if t == Identifier:
            return env.get(node.name, node.line)

        if t == BinaryOp:
            left = self._eval(node.left, env)
            right = self._eval(node.right, env)
            return self._apply_binop(left, node.op, right, node.line)

        if t == UnaryMinus:
            val = self._eval(node.expr, env)
            if not isinstance(val, (int, float)):
                raise BlossomRuntimeError(
                    f"You can only negate a number, but I got {self._to_display(val)!r}.",
                    node.line
                )
            return -val

        if t == Comparison:
            left = self._eval(node.left, env)
            right = self._eval(node.right, env)
            return self._apply_comparison(left, node.op, right, node.line)

        if t == ContainsExpr:
            collection = self._eval(node.collection, env)
            item = self._eval(node.item, env)
            if not isinstance(collection, (list, str)):
                raise BlossomRuntimeError(
                    f"'contains' only works on lists and text, not {self._to_display(collection)!r}.",
                    node.line
                )
            return item in collection

        if t == LogicalOp:
            left = self._eval(node.left, env)
            if node.op == 'and':
                return bool(left) and bool(self._eval(node.right, env))
            else:
                return bool(left) or bool(self._eval(node.right, env))

        if t == NotExpr:
            return not bool(self._eval(node.expr, env))

        if t == CallExpr:
            args = [self._eval(a, env) for a in node.args]
            return self._call_function(node.name, args, env, node.line)

        if t == IndexExpr:
            lst = env.get(node.name, node.line)
            idx = self._eval(node.index, env)
            if not isinstance(idx, (int, float)):
                raise BlossomRuntimeError(
                    f"List positions must be numbers, but I got {self._to_display(idx)!r}.",
                    node.line
                )
            idx = int(idx)
            if isinstance(lst, str):
                if idx < 1 or idx > len(lst):
                    raise BlossomRuntimeError(
                        f"Position {idx} is out of range. "
                        f"The text has {len(lst)} character(s), so valid positions are 1 to {len(lst)}.",
                        node.line
                    )
                return lst[idx - 1]
            if not isinstance(lst, list):
                raise BlossomRuntimeError(
                    f"'{node.name}' is not a list or text, so I can't get an item at a position.",
                    node.line
                )
            if idx < 1 or idx > len(lst):
                raise BlossomRuntimeError(
                    f"Position {idx} is out of range. "
                    f"The list has {len(lst)} item(s), so valid positions are 1 to {len(lst)}.",
                    node.line
                )
            return lst[idx - 1]

        if t == LengthExpr:
            val = env.get(node.name, node.line)
            if not isinstance(val, (list, str)):
                raise BlossomRuntimeError(
                    f"'length of' only works on lists and text, but '{node.name}' is {self._to_display(val)!r}.",
                    node.line
                )
            return len(val)

        if t == RandomExpr:
            low = self._eval(node.low, env)
            high = self._eval(node.high, env)
            if not isinstance(low, (int, float)) or not isinstance(high, (int, float)):
                raise BlossomRuntimeError(
                    "Random number bounds must be numbers.",
                    node.line
                )
            return _random.randint(int(low), int(high))

        if t == ConvertExpr:
            val = self._eval(node.expr, env)
            if node.target == 'number':
                try:
                    result = float(val)
                    return int(result) if result == int(result) else result
                except (ValueError, TypeError):
                    raise BlossomRuntimeError(
                        f"I can't convert {self._to_display(val)!r} to a number. "
                        "Make sure it's something like \"42\" or \"3.14\".",
                        node.line
                    )
            else:  # text
                return self._to_str(val)

        raise BlossomRuntimeError(f"Unknown expression type: {type(node).__name__}")

    # ── Function calls ────────────────────────────────────────────────────────

    def _call_function(self, name: str, args: list, env: Environment, line=None):
        if name not in self.functions:
            raise BlossomRuntimeError(
                f"I don't know a function called '{name}'. "
                "Did you define it with 'define'?",
                line
            )
        fn = self.functions[name]
        if len(args) != len(fn.params):
            raise BlossomRuntimeError(
                f"'{name}' needs {len(fn.params)} input(s) but I got {len(args)}.",
                line
            )
        local_env = Environment(parent=self.global_env)
        for param, arg in zip(fn.params, args):
            local_env.define(param, arg)
        try:
            self._exec_stmts(fn.body, local_env)
        except ReturnSignal as ret:
            return ret.value
        return None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_list(self, name: str, env: Environment, line=None) -> list:
        val = env.get(name, line)
        if not isinstance(val, list):
            raise BlossomRuntimeError(
                f"'{name}' is not a list. Create it first with 'make a list called {name}'.",
                line
            )
        return val

    def _apply_binop(self, left, op: str, right, line=None):
        if op == '+':
            # Auto-convert to string if either side is a string
            if isinstance(left, str) or isinstance(right, str):
                return self._to_str(left) + self._to_str(right)
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            raise BlossomRuntimeError(
                f"I can't add {self._to_display(left)!r} and {self._to_display(right)!r} together.",
                line
            )
        if op == '-':
            self._check_numbers(left, right, '-', line)
            return left - right
        if op == '*':
            self._check_numbers(left, right, '*', line)
            return left * right
        if op == '/':
            self._check_numbers(left, right, '/', line)
            if right == 0:
                raise BlossomRuntimeError(
                    "You can't divide by zero. The math doesn't work!",
                    line
                )
            result = left / right
            return int(result) if result == int(result) else result
        if op == '%':
            self._check_numbers(left, right, '%', line)
            if right == 0:
                raise BlossomRuntimeError("You can't use 0 with remainder (%).", line)
            return left % right

    def _apply_comparison(self, left, op: str, right, line=None):
        try:
            if op == '==':
                return left == right
            if op == '!=':
                return left != right
            if op == '>':
                return left > right
            if op == '<':
                return left < right
            if op == '>=':
                return left >= right
            if op == '<=':
                return left <= right
        except TypeError:
            raise BlossomRuntimeError(
                f"I can't compare {self._to_display(left)!r} and {self._to_display(right)!r}.",
                line
            )

    def _check_numbers(self, left, right, op: str, line=None):
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            op_names = {'-': 'subtract', '*': 'multiply', '/': 'divide', '%': 'get the remainder of'}
            verb = op_names.get(op, f"use '{op}' with")
            raise BlossomRuntimeError(
                f"You can only {verb} numbers. "
                f"I got {self._to_display(left)!r} and {self._to_display(right)!r}.",
                line
            )

    def _to_str(self, value) -> str:
        if value is None:
            return 'nothing'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value)

    def _to_display(self, value) -> str:
        if value is None:
            return 'nothing'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, list):
            return '[' + ', '.join(self._to_display(v) for v in value) + ']'
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value)
