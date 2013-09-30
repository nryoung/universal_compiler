"""
Grammer Analyzer implementation.
"""

class GrammarAnalyzer(object):

    def __init__(self, grammar):
        self.productions = grammar.readlines()

    def analyze(self):
        print "productions:"
        for prod in self.productions:
            print prod
