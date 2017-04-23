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
    def interpret(self, node, env):
        if node.type == Type.NUM:
            return self.interpret_num(node, env)

        elif node.type == Type.VAR:
            return self.interpret_var(node, value)

        elif node.type == Type.LAMBDA:
            return self.interpret_lambda(node, env)


    def interpret_num(self, node, env):
        return node.value

    def interpret_var(self, node, env):
        bound = env.look_up(node.value)
        if bound is None:
            raise UnBoundError
        return bound

    def interpret_call(self, node, env):
        closure = self.interpret(node, env)
        arg_values = [self.interpret(arg, env) for arg in node.children]

        env_save = closure.env
        expr_save = closure.expr

        args = self._interpret_arg_tuple(closure.args)

        scope = Scope.make_scope(args, arg_values)

        with env_save.ext_env(scope) as new_env:
            return self.interpret(expr_save, new_nev)

    def _interpret_arg_tuple(self, node):
        return [node.value] + [child.value for child in node.children]

    def interpret_bind(self, node, env):
        arg_value_pairs = self._interpret_bind_pair(node.children[0], env)
        scope = Scope.make_scope(arg_value_pairs)
        with env.ext_env(scope) as new_nev:
            return interpret(node.children[1], new_nev)

    def _interpret_bind_pair(self, node, env):
        arg = node.value
        val = self.interpret(node.children[0], env)
        return (arg, val)

    def interpret_lambda(self, node, env):
        return Closure(node, env)

    def interpret_if(self, node, env):
        cond_node, then_node, else_node = node.children
        if self.interpret(cond_node, env):
            return self.interpret(then_node, env)
        else:
            return self.interpret(else_node, env)

    def interpret_condition(self, node, env):
        left, value, right_value = (self.interpret(child, env) for child in node.children)
        if node.type == Type.EQ:
            return left_value == right_value
        elif node.type == Type.NEQ:
            return left_value != right_value
        elif node.type == Type.LT:
            return left_value < right_value
        elif node.type == Type.LTE:
            return left_value <= right_value
        elif node.type == Type.MT:
            return left_value > right_value
        elif node.type == Type.MTE:
            return left_value >= right_value

    def interpret_arithmetic(self, node, env):
        values = [self.interpret(child, env) for child in node.children]
        if len(values) >= 2:
            if node.type == Type.PLUS:
                return reduce(lambda x, y: x+y, values)
            elif node.type == Type.TIMES:
                return reduce(lambda x, y: x*y, values, 1)
            elif len(values) == 2:
                if node.type == Type.MINUS:
                    return values[0] - values[1]
                else:
                    return values[0] / values[1]
            else:
                raise SyntaxError

        elif len(values) == 1:
            if node.type == Type.MINUS:
                return values[0] * (-1)
            else:
                raise SyntaxError


def interpret_one_sentence(text):
    interpreter = Interpreter()
    return interpret(parse(text), Env())
