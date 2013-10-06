"""
Predict Generator implementation.
"""
from .grammar_analyzer import GrammarAnalyzer

class PredictGenerator(object):

    def __init__(self, prods):
        self.ga = GrammarAnalyzer(prods)
        self.derives_lambda = {}

    def mark_lambda(self):

        changes = True
        rhs_derives_lambda = None

        # construct this the crappy way at first
        for s in self.ga.symbols:
            self.derives_lambda[s] = False

        # explicitly mark lambda as True
        self.derives_lambda['lambda'] = True

        while changes:
            print self.derives_lambda
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
        k = len(x)
        if k == 0:
            result = set(['lambda'])
        else:
            result = first_set(x[0])
            result.remove('lambda')
            i = 0
            while i < k and 'lambda' in first_set(x[i]):
                i = i + 1
                result = result.union(first_set(x[i]))
                result.remove('lambda')
            if i == k and 'lambda' in first_set(x[k]):
                result = result.union(set(['lambda']))
        return result

    def generate(self):
        self.mark_lambda()
        print self.derives_lambda
