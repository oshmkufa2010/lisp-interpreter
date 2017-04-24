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
    NUM = 'NUM'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    TIMES = 'TIMES'
    DIVIDE = 'DIVIDE'
    LET = 'LET'
    LAMBDA = 'LAMBDA'
    VAR = 'VAR'
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    MT = 'MT'
    LTE = 'LTE'
    MTE = 'MTE'
    IF = 'IF'
    CALL = 'CALL'
    ARG_TUPLE = 'ARG_TUPLE'
    PARA_TUPLE = 'PARA_TUPLE'
    BIND_PAIR_TUPLE = 'BIND_PAIR_TUPLE'

    @classmethod
    def get_type_by_name(cls, name):
        return getattr(cls, name)


class AstNode(object):
    def __init__(self, node_type, node_value=None):
        self.type = token_type
        self.value = node_value


class AstNodeCreator(object):
    def __init__(self, cls):
        self.cls = cls

    def __getattr__(self, node_name):
        node_type = getattr(AstNodeType, node_name)
        return self.cls(node_type)


class SExpAST(AST):
    def __init__(self, node, children=None):
        self.__node = node
        self.__children = children or ()

    @classmethod
    def from_sexp(cls, sexp):

        # number or variable
        if isinstance(sexp, Token):
            if sexp.type == TokenType.NUM:
                return cls(AstNode(AstNodeType.NUM), sexp.value)
            elif sexp.type == TokenType.VAR:
                return cls(AstNode(AstNodeType.VAR), sexp.value)

        op = sexp[0]

        # call
        if isinstance(op, list) or op.type == TokenType.VAR:
            args = tuple(cls.from_sexp(child) for child in sexp[1:])
            args_node = AstNode(AstNodeType.ARG_TUPLE, args)
            args_ast = cls(args_node)

            fn_ast = cls.from_sexp(op)

            call_node = AstNode(AstNodeType.CALL, None)

            return cls(call_node, (fn_ast, args_ast))

        # lambda
        elif op.type == TokenType.LAMBDA:
            paras = tuple(para.value for para in sexp[1])
            paras_node = AstNode(AstNodeType.PARA_TUPLE, paras)

            paras_ast = cls(paras_node)

            body_ast = cls.from_sexp(sexp[2])

            lambda_node = AstNode(AstNodeType.LAMBDA, None)

            return cls(lambda_node, (paras_ast, body_ast))

        # let
        elif op.type == TokenType.LET:
            bind_pairs = tuple((pair[0].value, cls.from_sexp(pair[1])) for pair in sexp[1])
            bind_pairs_node = AstNode(AstNodeType.BIND_PAIR_TUPLE, bind_pairs)
            bind_pairs_ast = cls(bind_pairs_node)

            body_ast = cls.from_sexp(sexp[2])

            let_node = AstNode(AstNodeType.LET, None)

            return cls(let_node, (bind_pairs_ast, body_ast))

        # if
        elif op.type == TokenType.IF:
            children = tuple(cls.from_sexp(exp) for exp in sexp[1:])
            if_node = AstNode(AstNodeType.IF, None)
            return cls(if_node, children)

        elif op.type in (TokenType.EQ,
                         TokenType.NEQ,
                         TokenType.LT,
                         TokenType.LTE,
                         TokenType.MT,
                         TokenType.MTE
                         TokenType.PLUS,
                         TokenType.MINUS,
                         TokenType.TIMES,
                         TokenType.DIVIDE):
            node = AstNode(AstNodeType.get_type_by_name(op.type), None)
            children = tuple(cls.from_sexp(exp) for exp in sexp[1:])
            return cls(node, children)

        else:
            raise SyntaxError

    def left(self):
        try:
            return self.__children[0]
        except IndexError:
            return ()

    def right(self):
        try:
            return self.__children[1]
        except IndexError:
            return ()

    def children(self):
        return self.__children

    def __getattr__(self, attr):
        return getattr(self.__node, attr)
