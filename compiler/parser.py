"""
Parser implementation.
"""
from .scanner import Scanner
from .predict_generator import PredictGenerator

class Parser(object):

    def __init__(self, program, grammar, start_sym):
        self.scanner = Scanner(program)
        self.pg = PredictGenerator(grammar)
