"""
Predict Generator implementation.
"""
from .grammar_analyzer import GrammarAnalyzer

class PredictGenerator(object):

    def __init__(self, prods):
        self.ga = GrammarAnalyzer(prods)
        self.derives_lambda = {}
        self.first_sets = {}
        self.follow_sets = {}

    def mark_lambda(self):

        changes = True
        rhs_derives_lambda = None

        # construct this the crappy way at first
        for s in self.ga.symbols:
            self.derives_lambda[s] = False

        # explicitly mark lambda as True
        self.derives_lambda['lambda'] = True

        while changes:
            changes = False
            for p in self.ga.productions:
                rhs_derives_lambda = True
                lhs = self.ga.get_lhs(p)
                rhs = self.ga.get_rhs(p)

                for i in rhs:
                    rhs_derives_lambda = rhs_derives_lambda and self.derives_lambda[i]

                if rhs_derives_lambda and not self.derives_lambda[lhs]:
                    changes = True
                    self.derives_lambda[lhs] = True

    def compute_first(self, x):
        result = set()
        k = len(x)
        if k == 0:
            result = set(['lambda'])
        else:
            result = self.first_sets[x[0]]
            if 'lambda' in result:
                result.remove('lambda')
            i = 0
            while i < (k-1) and 'lambda' in self.first_sets[x[i]]:
                i = i + 1
                result = result.union(self.first_sets[x[i]])
                result.remove('lambda')
        if i == (k-1) and 'lambda' in self.first_sets[x[k-1]]:
            result = result.union(set(['lambda']))
        return result

    def fill_first_set(self):
        for A in self.ga.non_terminals:
            if self.derives_lambda[A]:
                self.first_sets[A] = set(['lambda'])
            else:
                self.first_sets[A] = set()

        for a in self.ga.terminals:
            self.first_sets[a] = set([a])
            for A in self.ga.non_terminals:
                if self.ga.matching(A, a):
                    self.first_sets[A] = self.first_sets[A].union(set([a]))

        changes = True
        fs_begin = {}
        while changes:
            fs_begin.update(self.first_sets)
            changes = False
            for p in self.ga.productions:
                lhs = self.ga.get_lhs(p)
                rhs_set = self.compute_first(self.ga.get_rhs(p))
                self.first_sets[lhs] = self.first_sets[lhs].union(rhs_set)

            if fs_begin != self.first_sets:
                changes = True

    def fill_follow_set(self, start_sym):
        for A in self.ga.non_terminals:
            self.follow_sets[A]= set()

        self.follow_sets[start_sym] = set(['lambda'])

        changes = True
        while changes:
            changes = False
            for p in self.ga.productions:
                A = self.ga.get_lhs(p)
                B = self.ga.get_b(p)
                y = self.ga.get_y(b, p)
                for nt in self.ga.get_rhs(p):
                    if B == nt:
                        self.follow_sets[B] = self.follow_sets[B].union(compute_first(y).remove('lambda'))
                    if 'lambda' in compute_first(y):
                        self.follow_sets[B] = self.follow_sets[B].union(self.follow_sets[A])


    def generate(self):
        self.mark_lambda()
        print "Derives Lambda:"
        print "---------------"
        for sym, dl  in sorted(self.derives_lambda.items()):
            print "%s : %s" % (sym, dl)

        self.fill_first_set()
        print "\nFirst Sets:"
        print "-----------"
        for sym, fs in sorted(self.first_sets.items()):
            if sym in self.ga.non_terminals:
                print "%s : {%s}" % (sym, ", ".join(f for f in fs))
