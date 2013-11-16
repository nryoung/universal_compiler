"""
Parser implementation.
"""
from .scanner import Scanner
from .predict_generator import PredictGenerator
from .compiler_errors import SyntaxError

class Parser(object):

    def __init__(self, program, grammar, start_sym):
        self.scanner = Scanner(program)
        self.pg = PredictGenerator(grammar)
        self.start_sym = start_sym
        self.stack = []
        self.ss_stack = []
        self.gen_code = ''
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

    def _display_compile(self, idx):
        print "Remaining Input:"
        print self.scanner.micro_lang.replace('\n', '')
        print "Parse Stack:"
        print self.stack[::-1]
        print "Semantic Stack:"
        print self.ss_stack[::-1]
        print "Generated Code:"
        print self.gen_code
        print "Indices:"
        print "(%s, %s, %s, %s)" % (idx[0], idx[1], idx[2], idx[3])
        print '-' * 80

    def ll_driver(self):
        self.stack.append(self.start_sym)
        a = self.scanner.scan()

        while self.stack:
            X = self.stack[-1]

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
                            raise SyntaxError(a)

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
                    raise SyntaxError(a)

    def ll_compiler(self):
        token_text, a = self.scanner.scan()

        # push start symbol on both stacks
        self.stack.append(self.start_sym)
        self.ss_stack.append(self.start_sym)
        left_idx = 0
        right_idx = 0
        current_idx = 0
        top_idx = 1

        # now we start our loop
        while self.stack:
            X = self.stack[-1]

            print "X: %s" % str(X)
            print "a: ", a

            if a == 'EmptySpace' or a == 'Comment':
                token_text, a = self.scanner.scan()
                continue

            if X == 'lambda':
                self.stack.pop()
                continue

            self._display_compile((left_idx, right_idx, current_idx, top_idx))
            # X is a non-terminal we have to process it
            if X in self.pg.ga.get_non_terminals():
                col = self.rev_tk_mapping[a]
                col_num = self.pg.col_matching[col]

                self.stack.pop()
                # Push EOP, a tuple in this case, on to the parse stack
                self.stack.append((left_idx, right_idx, current_idx, top_idx))

                # Now we need to grab the prodcutions Y_m...Y_1 and push them on
                # both stacks.
                new_X = None
                perdict_num = None
                for row in self.pg.predict_tbl:
                    if X == row[0]:
                        if row[col_num] != ' ':
                            predict_num = row[col_num]
                            new_X = self.pg.ga.productions[row[col_num] - 1]
                            new_X = self.pg.ga.get_rhs(new_X, action=True)
                        else:
                            print "X: %s" % X
                            print "In first else, where it is a non term and not matched."
                            raise SyntaxError(a)

                for x in new_X[::-1]:
                    # only push non action symbols on the SS stack
                    if '#' not in x:
                        self.ss_stack.append(x)
                    # Push everything on the Parse stack
                    self.stack.append(x)

                left_idx = current_idx
                right_idx = top_idx
                current_idx = right_idx
                top_idx = top_idx + (len(new_X) - 1)



            # X is terminal
            elif X in self.pg.ga.get_terminals():
                print "Terminal"
                if X == self.rev_tk_mapping[a]:
                    self.ss_stack[current_idx] = token_text
                    self.stack.pop()
                    token_text, a = self.scanner.scan()
                    current_idx += 1
                else:
                    print "In second else, where it is a terminal and not matched"
                    raise SyntaxError(a)

            # X is EOP
            elif type(X) == tuple:
                print "EOP"
                left_idx = X[0]
                right_idx = X[1]
                current_idx = X[2]
                top_idx = X[3]

                current_idx += 1

                self.stack.pop()

            # X is action symbol
            else:
                print "X is action symbol: %s" % X
                self.stack.pop()
                # call semantic record here, somehow.
