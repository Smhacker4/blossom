from enum import Enum, auto


class TT(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()

    # Identifier
    NAME = auto()

    # Keywords
    SAY = auto()
    SET = auto()
    TO = auto()
    ASK = auto()
    AND = auto()
    STORE = auto()
    IN = auto()
    IF = auto()
    IS = auto()
    GREATER = auto()
    LESS = auto()
    THAN = auto()
    OTHERWISE = auto()
    REPEAT = auto()
    TIMES = auto()
    WHILE = auto()
    MAKE = auto()
    A = auto()
    LIST = auto()
    CALLED = auto()
    ADD = auto()
    FOR = auto()
    EACH = auto()
    DEFINE = auto()
    WITH = auto()
    CALL = auto()
    GIVE = auto()
    BACK = auto()
    NOT = auto()
    TRUE = auto()
    FALSE = auto()
    OR = auto()
    EQUAL = auto()
    AT = auto()
    LEAST = auto()
    MOST = auto()
    LENGTH = auto()
    OF = auto()
    CONTAINS = auto()
    BETWEEN = auto()
    RANDOM = auto()
    NUMBER_KW = auto()
    TEXT = auto()
    CONVERT = auto()
    REMOVE = auto()
    FROM = auto()
    NOTHING = auto()
    THEN = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()

    # Punctuation
    COLON = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()

    # Structure
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


KEYWORDS = {
    'say': TT.SAY,
    'set': TT.SET,
    'to': TT.TO,
    'ask': TT.ASK,
    'and': TT.AND,
    'store': TT.STORE,
    'in': TT.IN,
    'if': TT.IF,
    'is': TT.IS,
    'greater': TT.GREATER,
    'less': TT.LESS,
    'than': TT.THAN,
    'otherwise': TT.OTHERWISE,
    'repeat': TT.REPEAT,
    'times': TT.TIMES,
    'while': TT.WHILE,
    'make': TT.MAKE,
    'a': TT.A,
    'list': TT.LIST,
    'called': TT.CALLED,
    'add': TT.ADD,
    'for': TT.FOR,
    'each': TT.EACH,
    'define': TT.DEFINE,
    'with': TT.WITH,
    'call': TT.CALL,
    'give': TT.GIVE,
    'back': TT.BACK,
    'not': TT.NOT,
    'true': TT.TRUE,
    'false': TT.FALSE,
    'or': TT.OR,
    'equal': TT.EQUAL,
    'at': TT.AT,
    'least': TT.LEAST,
    'most': TT.MOST,
    'length': TT.LENGTH,
    'of': TT.OF,
    'contains': TT.CONTAINS,
    'between': TT.BETWEEN,
    'random': TT.RANDOM,
    'number': TT.NUMBER_KW,
    'text': TT.TEXT,
    'convert': TT.CONVERT,
    'remove': TT.REMOVE,
    'from': TT.FROM,
    'nothing': TT.NOTHING,
    'then': TT.THEN,
}


class Token:
    def __init__(self, type: TT, value, line: int):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f'Token({self.type.name}, {self.value!r}, L{self.line})'
