"""
Semantic routines for the universal compiler.
"""
from aux_routines import generate
from aux_routines import extract
from aux_routines import extract_op
from aux_routines import get_temp
from aux_routines import check_id
from aux_routines import extract_sem
from data_structures import ExprRec, OpRec

def start(symbol_table):
    symbol_table[:] = []

def assign(target, source):
    generate("STORE", extract_sem(source), target.name)

def read_id(invar):
    generate("READ", invar.name, "Integer")

def write_expr(outexpr):
    generate("WRITE", extract_sem(outexpr), "Integer")

def gen_infix(e1, op, e2, symbol_table):
    temp_expr = ExprRec(get_temp(symbol_table))
    generate(extract_sem(op), extract_sem(e1), extract_sem(e2), temp_expr.name)
    return temp_expr

def process_id(e, token_buffer, symbol_table):
    ### See how this is used before editing
    check_id(token_buffer, symbol_table)
    e.name = token_buffer

def proc_literal(e, token_buffer):
    ### See how this is used before editing
    # mocking token buffer here too
    e.val = int(token_buffer)

def process_op(o, current_token):
    # mocking current token
    o.op = current_token

def finish():
    generate("HALT")
