"""
Data structures to be used in the universal compiler.
"""

from compiler_errors import OpError
from compiler_errors import LiteralError
from compiler_errors import IdError
from compiler_errors import SyntaxError

class OpRec(object):

    allowed_vals = ['-', '+', None]

    def __init__(self, operator=None):
        self.op = operator

    @property
    def op(self):
        return self._op

    @op.setter
    def op(self, o):
        if o not in self.allowed_vals:
            raise OpError("Operator must either be a '+' or '-'")
        else:
            self._op = o

class ExprRec(object):

    def __init__(self, val):
        self.val = val


def sem_rec(s):
    op_rec_vals = ('-', '+', None)
    if s in op_rec_vals:
        return OpRec(s)
    elif s.isdigit():
        return ExprRec(int(s))
    else:
        return ExprRec(s)
