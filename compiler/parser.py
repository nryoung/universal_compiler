"""
Parser implementation.
"""
from .scanner import Scanner
from .predict_generator import PredictGenerator

class Parser(object):

    def __init__(self, program, grammar, start_sym):
        self.scanner = Scanner(program)
        self.pg = PredictGenerator(grammar)
        self.start_sym = start_sym
        self.stack = []
        self.pg.generate_predict_table(self.start_sym)

        self.rev_tk_mapping = { 'Id': 'Id', 'IntLiteral': 'IntLiteral', 'PlusOp': '+',
                              'AssignOp': ':=', 'Comma': ',', 'SemiColon': ';',
                              'LParen': '(', 'RParen': ')', 'MinusOp': '-', 'EofSym': '$',
                              'BeginSym': 'begin', 'EndSym': 'end', 'ReadSym': 'read',
                              'WriteSym': 'write', 'EmptySpace': ' ', 'Comment': ''
                              }


    def _display_row(self, a, pn=None):
        if pn:
            print "Parser Action:"
            print "Predict", pn 
            print "Remaining Input:"
            print self.rev_tk_mapping[a].upper() + self.scanner.micro_lang.replace('\n', ' ')
            print "Parse Stack:" 
            print self.stack[::-1]
            print '-' * 80
        else:
            print "Parser Action:"
            print "Match"
            print "Remaining Input:"
            print self.rev_tk_mapping[a].upper() + self.scanner.micro_lang.replace('\n', ' ')
            print "Parse Stack:"
            print self.stack[::-1]
            print '-' * 80

    def ll_driver(self):
        self.stack.append(self.start_sym)
        a = self.scanner.scan()

        while self.stack:
            X = self.stack[-1]
            #print "X: %s, a: %s" % (X, a)

            # Unfortunately the predict table does not account for empty space
            if a == 'EmptySpace' or a == 'Comment':
                a = self.scanner.scan()
                continue

            # Doesn't account for lambda either? hmmm
            if X == 'lambda':
                self.stack.pop()
                continue

            if X in self.pg.ga.get_non_terminals():
                # from the token yielded from scanner we need to map to correct col
                # thus we do this by do calls to correct dicts
                col = self.rev_tk_mapping[a]
                col_num = self.pg.col_matching[col]

                # Now we have to iterate through the table to find the right row.
                # perhaps a func can be made in pg to do this?
                new_X = None
                predict_num = None
                for row in self.pg.predict_tbl:
                    if X == row[0]:
                        if row[col_num] != ' ':
                            predict_num = row[col_num]
                            new_X = self.pg.ga.productions[row[col_num] - 1]
                            new_X = self.pg.ga.get_rhs(new_X)
                        else:
                            print "RAISE SYNTAX ERROR HERE!"
                            return

                self._display_row(a, pn=predict_num)
                # pop the items of the stack and replace them with new stuff
                self.stack.pop()
                for x in new_X[::-1]:
                    self.stack.append(x)


            elif X in self.pg.ga.get_terminals():
                if X == self.rev_tk_mapping[a]:
                    self._display_row(a)
                    self.stack.pop()
                    a = self.scanner.scan()
                else:
                    print "RAISE SYTNAX ERROR"
                    return
