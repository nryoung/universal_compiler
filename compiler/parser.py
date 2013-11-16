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

    def _call_action(self, X):
        action = X.split('#')[1].lower()
        eval("self." + action)


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
                self._call_action(X)


    # All of the semantic routine start here
    def start(self):
        pass

    def assign(self, target, source):
        generate("STORE", extract_sem(source), target.name)

    def read_id(self, invar):
        generate("READ", invar.name, "Integer")

    def write_expr(self, outexpr):
        generate("WRITE", extract_sem(outexpr), "Integer")

    def gen_infix(self, e1, op, e2, symbol_table):
        temp_expr = ExprRec(get_temp(symbol_table))
        generate(extract_sem(op), extract_sem(e1), extract_sem(e2), temp_expr.name)
        return temp_expr

    def process_id(self):
        ### See how this is used before editing
        check_id(token_buffer, symbol_table)
        e.name = token_buffer

    def proc_literal(self, e, token_buffer):
        ### See how this is used before editing
        # mocking token buffer here too
        e.val = int(token_buffer)

    def process_op(self, o, current_token):
        # mocking current token
        o.op = current_token

    def finish(self):
        generate("HALT")

    # All of the aux routines
    def generate(s1, s2=None, s3=None, s4=None):
        if s4:
            sys.stdout.write("%s %s, %s, %s\n" % (s1, s2, s3, s4))
        elif s3:
            sys.stdout.write("%s %s, %s\n" % (s1, s2, s3))
        else:
            sys.stdout.write("%s" % s1)

    def extract_sem(s):
        rec = sem_rec(s)
        if rec is ExprRec:
            return extract(sem_rec)
        elif rec is OpRec:
            return extract_op(sem_rec)
        else:
            raise SyntaxError

    def extract(e):
        if e.name:
            return str(e.name)
        else:
            return int(e.val)

    def extract_op(o):
        if o.op == "+":
            return "ADD"
        else:
            return "SUB"

    def look_up(s, symbol_table):
        if s in symbol_table:
            return  True
        else:
            return False

    def enter(s, symbol_table):
        symbol_table.append(s)

    def check_id(s, symbol_table):
        if not look_up(s, symbol_table):
            enter(s, symbol_table)
            generate("DECLARE", s, "Integer")

    def get_temp(symbol_table):
        global max_temp
        max_temp += 1

        temp_name = "Temp&%s" % max_temp
        check_id(temp_name, symbol_table)
        return temp_name
