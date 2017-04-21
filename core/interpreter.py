# coding=utf-8


from contextlib import contextmanager
import copy
from errors import UnBoundError
from parser import parse, Token, Type


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
    def ext_env(self, scope=None):
        if scope:
            self.__scopes.append(scope)
            yield self
            self.__scopes.pop()
        else:
            yield self


class Scope(dict):
    @classmethod
    def make_scope(cls, args, arg_values):
        kwargs = {}
        for arg, value in zip(args, arg_values):
            kwargs.update({arg: value})
        return cls(kwargs)


class Closure(object):
    def __init__(self, expr, env):
        self.__expr = expr
        self.__env = copy.deepcopy(env)

    @property
    def env(self):
        return self.__env

    @property
    def expr(self):
        return self.__expr[2]

    @property
    def args(self):
        return self.__expr[1]


def interpret_arg_tuple(arg_tuple):
    if not arg_tuple:
        return None

    if isinstance(arg_tuple, Token):
        arg_tuple = [arg_tuple]

    return [arg.value for arg in arg_tuple]


def interpret(expr, env):
    if not expr:
        return 0

    if isinstance(expr, Token) or len(expr) == 1:
        if len(expr) == 1:
            expr = expr[0]
        if expr.type == Type.NUM:
            return expr.value
        elif expr.type == Type.VAR:
            bound = env.look_up(expr.value)
            if bound is None:
                raise UnBoundError
            return bound

    op = expr[0]
    # call
    if isinstance(op, list) or (isinstance(op, Token) and op.type == Type.VAR):
        closure = interpret(expr[0], env)
        arg_values = [interpret(arg, env) for arg in expr[1:]]
        if isinstance(closure, Closure):
            env_save = closure.env
            expr_save = closure.expr

            args = interpret_arg_tuple(closure.args)
            scope = Scope.make_scope(args, arg_values)

            with env_save.ext_env(scope) as new_env:
                result = interpret(expr_save, new_env)
            return result

    # expamle: (let (x v) (+ x 1))
    if op.type == Type.LET:
        bind_pair = expr[1]
        val = interpret(bind_pair[1], env)
        arg = bind_pair[0].value
        scope = Scope.make_scope((arg,), (val,))
        with env.ext_env(scope) as new_env:
            result = interpret(expr[2], new_env)
        return result

    # example: (lambda (x) (+ x 1))
    elif op.type == Type.LAMBDA:
        return Closure(expr, env)

    elif op.type == Type.IF:
        try:
            cond_expr, then_expr, else_expr = expr[1:]
        except ValueError:
            raise SyntaxError
        else:
            result = interpret(cond_expr, env)
            if result:
                return interpret(then_expr, env)
            else:
                return interpret(else_expr, env)

    elif op.type in (Type.EQ, Type.NEQ, Type.LT, Type.LTE, Type.MT, Type.MTE):
        try:
            left_value, right_value = (interpret(exp, env) for exp in expr[1:])
        except ValueError:
            raise SyntaxError
        else:
            if op.type == Type.EQ:
                return left_value == right_value
            elif op.type == Type.NEQ:
                return left_value != right_value
            elif op.type == Type.LT:
                return left_value < right_value
            elif op.type == Type.LTE:
                return left_value <= right_value
            elif op.type == Type.MT:
                return left_value > right_value
            elif op.type == Type.MTE:
                return left_value >= right_value
            else:
                raise SyntaxError

    elif op.type in (Type.PLUS, Type.MINUS, Type.TIMES, Type.DIVIDE):

        values = [interpret(exp, env) for exp in expr[1:]]

        if len(values) >= 2:
            if op.type == Type.PLUS:
                return reduce(lambda x, y: x+y, values)
            elif op.type == Type.TIMES:
                return reduce(lambda x, y: x*y, values, 1)
            elif len(values) == 2:
                if op.type == Type.MINUS:
                    return values[0] - values[1]
                else:
                    return values[0] / values[1]
            else:
                raise SyntaxError

        elif len(values) == 1:
            if op.type == Type.MINUS:
                return values[0] * (-1)
            else:
                raise SyntaxError

    else:
        raise SyntaxError


def interpret_one_sentence(text):
    return interpret(parse(text), Env())
