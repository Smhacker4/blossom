from dataclasses import dataclass, field
from typing import Any, Optional


# ── Expressions ──────────────────────────────────────────────────────────────

@dataclass
class NumberLit:
    value: float
    line: int = 0

@dataclass
class StringLit:
    value: str
    line: int = 0

@dataclass
class BoolLit:
    value: bool
    line: int = 0

@dataclass
class NothingLit:
    line: int = 0

@dataclass
class Identifier:
    name: str
    line: int = 0

@dataclass
class BinaryOp:
    left: Any
    op: str         # '+', '-', '*', '/', '%'
    right: Any
    line: int = 0

@dataclass
class UnaryMinus:
    expr: Any
    line: int = 0

@dataclass
class Comparison:
    left: Any
    op: str         # '==', '!=', '>', '<', '>=', '<='
    right: Any
    line: int = 0

@dataclass
class ContainsExpr:
    collection: Any
    item: Any
    line: int = 0

@dataclass
class LogicalOp:
    left: Any
    op: str         # 'and', 'or'
    right: Any
    line: int = 0

@dataclass
class NotExpr:
    expr: Any
    line: int = 0

@dataclass
class CallExpr:
    name: str
    args: list
    line: int = 0

@dataclass
class IndexExpr:
    name: str
    index: Any
    line: int = 0

@dataclass
class LengthExpr:
    name: str
    line: int = 0

@dataclass
class RandomExpr:
    low: Any
    high: Any
    line: int = 0

@dataclass
class ConvertExpr:
    expr: Any
    target: str     # 'number' or 'text'
    line: int = 0


# ── Statements ────────────────────────────────────────────────────────────────

@dataclass
class SayStmt:
    expr: Any
    line: int = 0

@dataclass
class SetStmt:
    name: str
    expr: Any
    line: int = 0

@dataclass
class AskStmt:
    prompt: Any
    var_name: str
    line: int = 0

@dataclass
class IfStmt:
    condition: Any
    body: list
    elseifs: list       # list of (condition, body) tuples
    else_body: Optional[list]
    line: int = 0

@dataclass
class RepeatTimesStmt:
    count: Any
    body: list
    line: int = 0

@dataclass
class RepeatWhileStmt:
    condition: Any
    body: list
    line: int = 0

@dataclass
class MakeListStmt:
    name: str
    items: list     # may be empty
    line: int = 0

@dataclass
class AddToListStmt:
    expr: Any
    list_name: str
    line: int = 0

@dataclass
class RemoveFromListStmt:
    expr: Any
    list_name: str
    line: int = 0

@dataclass
class ForEachStmt:
    var: str
    list_name: str
    body: list
    line: int = 0

@dataclass
class DefineStmt:
    name: str
    params: list
    body: list
    line: int = 0

@dataclass
class CallStmt:
    name: str
    args: list
    line: int = 0

@dataclass
class GiveBackStmt:
    expr: Any       # None means 'give back nothing'
    line: int = 0

@dataclass
class Program:
    stmts: list
