"""
Grammer Analyzer implementation.
"""

class GrammarAnalyzer(object):

    def __init__(self, grammar):
        self.productions = grammar.readlines()

    def get_symbols(self):
        g = self.productions
        symbols = set()

        for prod in g:
            sym = prod.split()
            sym.remove('->')
            symbols.update(sym)
        return symbols





    def analyze(self):
        symbols = self.get_symbols()

        print "productions:"
        for prod in self.productions:
            print prod

        print "symbols:"
        for sym in symbols:
            print sym
