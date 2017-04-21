import re
import collections


# Token specification
NUM = r'(?P<NUM>\d+\.*\d*)'

PLUS = r'(?P<PLUS>\+)'
MINUS = r'(?P<MINUS>-)'
TIMES = r'(?P<TIMES>\*)'
DIVIDE = r'(?P<DIVIDE>/)'


LPAREN = r'(?P<LPAREN>\()'
RPAREN = r'(?P<RPAREN>\))'
WS = r'(?P<WS>\s+)'
VAR = r'(?P<VAR>[a-zA-Z]+[a-zA-Z0-9]*)'

EQ = r'(?P<EQ>=)'
NEQ = r'(?P<NEQ>!=)'
LT = r'(?P<LT>\<)'
MT = r'(?P<MT>\>)'
LTE = r'(?P<LTE>\<=)'
MTE = r'(?P<MTE>\>=)'


master_pat = re.compile('|'.join([NUM,
                                  PLUS,
                                  MINUS,
                                  TIMES,
                                  DIVIDE,
                                  LPAREN,
                                  RPAREN,
                                  WS,
                                  VAR,
                                  EQ,
                                  NEQ,
                                  LTE,
                                  LT,
                                  MTE,
                                  MT]))

# Tokenizer
Token = collections.namedtuple('Token', ['type', 'value'])


class Type(object):

    __slots__ = ()

    NUM = 'NUM'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    TIMES = 'TIMES'
    DIVIDE = 'DIVIDE'
    LET = 'LET'
    LAMBDA = 'LAMBDA'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    VAR = 'VAR'
    WS = 'WS'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    MT = 'MT'
    LTE = 'LTE'
    MTE = 'MTE'
    IF = 'IF'


KEY_WORDS = {
    'lambda': Type.LAMBDA,
    'let': Type.LET,
    'if': Type.IF
}


class TokenList(object):
    """
    This class is a wrapper for a generator,
    which makes a generator used like a list
    """
    def __init__(self, fn):
        self.__fn = fn
        self.__generator = None
        self.__head = None

    def __call__(self, text):
        self.__generator = self.__fn(text)
        self.__head = self.__generator.next()
        return self

    def pop_head(self):
        """
        pop and return the first element of this list
        """
        ret = self.__head
        try:
            self.__head = self.__generator.next()
        except StopIteration:
            self.__head = None
        return ret

    def head(self):
        """
        just return the first element of this list
        """
        return self.__head


@TokenList
def generate_tokens(text):
    scanner = master_pat.scanner(text)
    for m in iter(scanner.match, None):
        tok = Token(m.lastgroup, m.group())
        if tok.type != Type.WS:
            if tok.type == Type.VAR:
                yield Token(KEY_WORDS.get(tok.value) or tok.type, tok.value)
            else:
                yield tok


def atom(token):
    if token.type == Type.NUM:
        try:
            return Token(token.type, int(token.value))
        except ValueError:
            return Token(token.type, float(token.value))
    elif token.type in (Type.VAR,
                        Type.PLUS,
                        Type.MINUS,
                        Type.TIMES,
                        Type.DIVIDE,
                        Type.EQ,
                        Type.NEQ,
                        Type.LT,
                        Type.LTE,
                        Type.MT,
                        Type.MTE) + tuple(KEY_WORDS.values()):
        return token
    else:
        raise SyntaxError(token)


def read_from(tokens):
    tok = tokens.pop_head()
    if tok is None:
        return
    if tok.type == Type.LPAREN:
        lst = []
        while tokens.head() and tokens.head().type != Type.RPAREN:
            lst.append(read_from(tokens))
        if tokens.pop_head() is None:
            raise SyntaxError
        return lst
    elif tok.type == Type.RPAREN:
        raise SyntaxError
    else:
        return atom(tok)


def parse(text):
    tokens = generate_tokens(text)
    expr = read_from(tokens)
    return expr
