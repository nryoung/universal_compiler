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


    def get_non_terminals(self):
        g = self.productions
        nt_list = []
        non_terminals = set()

        for prod in g:
            nt = ''
            for c in prod:
                if c == ' ':
                    break
                else:
                    nt += c
            nt_list.append(nt)
        non_terminals.update(nt_list)

        return non_terminals


    def analyze(self):
        symbols = self.get_symbols()
        non_terminals = self.get_non_terminals()

        print "productions:"
        print "------------"
        for prod in self.productions:
            print prod

        print "symbols:"
        print "--------"
        for sym in symbols:
            print sym

        print "non terminals:"
        print "--------------"
        for nt in non_terminals:
            print nt
