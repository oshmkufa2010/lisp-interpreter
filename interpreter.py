# coding=utf-8

import re
import collections
from contextlib import contextmanager
import copy

KEY_WORDS = ['lambda', 'let']

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

master_pat = re.compile('|'.join([NUM, PLUS, MINUS, TIMES,
                                  DIVIDE, LPAREN, RPAREN, WS, VAR]))
# Tokenizer
Token = collections.namedtuple('Token', ['type', 'value'])


class Type(object):

    __slots__ = []

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
                if tok.value == 'lambda':
                    yield Token(Type.LAMBDA, tok.value)
                elif tok.value == 'let':
                    yield Token(Type.LET, tok.value)
                else:
                    yield tok
            else:
                yield tok


class Env(object):
    def __init__(self, scopes=None):
        if isinstance(scopes, list):
            self.__scopes = copy.deepcopy(scopes)
        else:
            self.__scopes = []

    def look_up(self, var):
        for scope in self.__scopes[::-1]:
            bound = scope.get(var, None)
            if bound is not None:
                return bound
        return None

    @contextmanager
    def ext_env(self, var=None, val=None):
        if var and val:
            self.__scopes.append({var: val})
            yield self
            self.__scopes.pop()
        else:
            yield self


class Closure(object):
    def __init__(self, expr, env):
        self.__expr = expr
        self.__env = copy.deepcopy(env)

    @property
    def env(self):
        return self.__env

    @property
    def expr(self):
        return self.__expr

    @property
    def args(self):
        return self.__expr[1]


def atom(token):
    if token.type == Type.NUM:
        try:
            return Token(token.type, int(token.value))
        except ValueError:
            return Token(token.type, float(token.value))
    elif token.type in [Type.VAR, Type.PLUS, Type.MINUS, Type.TIMES, Type.DIVIDE, Type.LAMBDA, Type.LET]:
        return token
    else:
        raise SyntaxError


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


def interpret(expr, env):
    if not expr:
        return 0

    if isinstance(expr, Token):
        if expr.type == Type.NUM:
            return expr.value
        elif expr.type == Type.VAR:
            bound = env.look_up(expr.value)
            if bound is None:
                raise SyntaxError
            return bound

    op = expr[0]

    # call
    if isinstance(op, list) or (isinstance(op, Token) and op.type == Type.VAR):
        fn = interpret(expr[0], env)
        arg = interpret(expr[1], env)
        if isinstance(fn, Closure):
            env_save = fn.env
            expr_save = fn.expr
            arg_save = fn.args.value
            with env_save.ext_env(arg_save, arg) as new_env:
                result = interpret(expr_save[2], new_env)
            return result

    # expamle: (let (x v) (+ x 1))
    if op.type == Type.LET:
        bind_pair = expr[1]
        val = interpret(bind_pair[1], env)
        arg = bind_pair[0].value
        with env.ext_env(arg, val) as new_env:
            result = interpret(expr[2], new_env)
        return result

    # example: (lambda (x) (+ x 1))
    elif op.type == Type.LAMBDA:
        return Closure(expr, env)

    elif op.type in [Type.PLUS, Type.MINUS, Type.TIMES, Type.DIVIDE]:
        v1 = interpret(expr[1], env)
        v2 = interpret(expr[2], env)
        if op.type == Type.PLUS:
            return v1 + v2
        elif op.type == Type.MINUS:
            return v1 - v2
        elif op.type == Type.TIMES:
            return v1 * v2
        elif op.type == Type.DIVIDE:
            return v1 / v2

    else:
        raise SyntaxError


if __name__ == '__main__':
    expr1 = """
    ((lambda x (* 2 x)) 3)
    """
    expr2 = """
    (let (x 2) (* x 3))
    """
    expr3 = """
    (let (x 2)
        (let (f (lambda y (* x y)))
            (let (x 4)
                (f 3))))
    """
    expr4 = """
    (let (x 2)
        (let (f (lambda y (* x y)))
            (f 3)))
    """
    for expr in [expr1, expr2, expr3, expr4]:
        result = interpret(parse(expr), Env())
        assert result == 6
