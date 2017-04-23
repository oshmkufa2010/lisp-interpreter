from abc import ABCMeta, abstractmethod
import collections
from parser import Type as TokenType

class AST(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def left(self):
        pass

    @abstractmethod
    def right(self):
        pass

    @abstractmethod
    def children(self):
        pass


class AstNodeType(object):
    PLUS = 0
    MINUS = 1
    TIMES = 2
    DIVIDE = 3
    VAR = 4
    LET = 5
    LAMBDA = 6
    CALL = 7
    ARG_TUPLE = 8
    VALUE_TUPLE = 9
    BIND_PAIR = 10
    BIND_PAIR_TUPLE = 11


class AstNode(object):
    def __init__(self, token_type, token_value=None):
        pass


class SExpAST(AST):
    def __init__(self, node, children=None):
        self.__node = node
        self.__children = children or []

    @classmethod
    def from_sexp(cls, sexp):
        if isinstance(sexp, Token):
            pass
        op = sexp[0]
        # call
        if isinstance(op, list) or op.type == TokenType.VAR:
            args_node = AstNode(AstNodeType.ARG_TUPLE, None)
            args_children = [cls.from_sexp(child) for child in sexp[1:]]
            args_ast = cls(args_node, args_children)

            fn_ast = cls.from_sexp(op)

            children = [fn_ast, args_ast]

            call_node = AstNode(AstNodeType.CALL, None)

            return cls(call_node, children)

        else:
            pass

    def left(self):
        return self.__sexp[1]

    def right(self):
        return self.__sexp[2]

    def children(self):

        return self.__sexp[1:]

    def __getattr__(self, attr):
        return getattr(self.__node, attr)
