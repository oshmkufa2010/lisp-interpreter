# coding=utf-8


from contextlib import contextmanager
import copy
from errors import UnBoundError
from parser import parse, Token
from ast import AstNodeType as Type


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

    def __repr__(self):
        return str(self.__scopes)


class Scope(dict):
    @classmethod
    def make_scope(cls, arg_value_pairs):
        kwargs = {}
        for arg, value in arg_value_pairs:
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

    def __repr__(self):
        return '<expr:{0}, env:{1}>'.format(self.expr, str(self.__env))


class Interpreter(object):
    def interpret(self, ast, env=None):
        if env is None:
            env = Env()
        method_name = 'interpret_' + ast.type.lower()
        method = getattr(self, method_name)
        if method:
            return method(ast, env)
        else:
            if ast.type in (Type.PLUS,):
                pass


    def interpret_num(self, ast, env):
        return ast.value

    def interpret_var(self, ast, env):
        bound = env.look_up(ast.value)
        if bound is None:
            raise UnBoundError
        return bound

    def interpret_call(self, ast, env):
        closure = self.interpret(ast.children[0], env)
        arg_values = [self.interpret(arg, env) for arg in ast.children]

        env_save = closure.env
        expr_save = closure.expr

        args = self._interpret_arg_tuple(closure.args)

        scope = Scope.make_scope(args, arg_values)

        with env_save.ext_env(scope) as new_env:
            return self.interpret(expr_save, new_nev)

    def inpterpret_arg_tuple(self, ast, env):
        return tuple(self.interpret(arg, env) for arg in ast.value)

    def interpret_para_tuple(self, ast, env):
        return ast.value

    def interpret_bind_pair_tuple(self, ast, env):
        return tuple((pair[0], self.interpret(pair[1], env)) for pair in ast.value)


    def interpret_let(self, ast, env):
        arg_value_pairs = self.interpret(ast.children[0], env)
        scope = Scope.make_scope(arg_value_pairs)
        with env.ext_env(scope) as new_nev:
            return self.interpret(ast.children[1], new_nev)


    def interpret_lambda(self, ast, env):
        return Closure(ast.children, env)

    def interpret_if(self, ast, env):
        cond_ast, then_ast, else_ast = ast.children
        if self.interpret(cond_ast, env):
            return self.interpret(then_ast, env)
        else:
            return self.interpret(else_ast, env)

    def interpret_condition(self, ast, env):
        left, value, right_value = (self.interpret(child, env) for child in ast.children)
        if ast.type == Type.EQ:
            return left_value == right_value
        elif ast.type == Type.NEQ:
            return left_value != right_value
        elif ast.type == Type.LT:
            return left_value < right_value
        elif ast.type == Type.LTE:
            return left_value <= right_value
        elif ast.type == Type.MT:
            return left_value > right_value
        elif ast.type == Type.MTE:
            return left_value >= right_value

    def interpret_arithmetic(self, ast, env):
        values = [self.interpret(child, env) for child in ast.children]
        if len(values) >= 2:
            if ast.type == Type.PLUS:
                return reduce(lambda x, y: x+y, values)
            elif ast.type == Type.TIMES:
                return reduce(lambda x, y: x*y, values, 1)
            elif len(values) == 2:
                if ast.type == Type.MINUS:
                    return values[0] - values[1]
                else:
                    return values[0] / values[1]
            else:
                raise SyntaxError

        elif len(values) == 1:
            if ast.type == Type.MINUS:
                return values[0] * (-1)
            else:
                raise SyntaxError


def interpret_one_sentence(text):
    interpreter = Interpreter()
    return interpret(parse(text), Env())
