"""
Parser implementation.
"""
from .scanner import Scanner
from .predict_generator import PredictGenerator
from .compiler_errors import SyntaxError
from .data_structures import sem_rec, ExprRec, OpRec

class Parser(object):

    def __init__(self, program, grammar, start_sym, output):
        self.scanner = Scanner(program)
        self.pg = PredictGenerator(grammar)
        self.start_sym = start_sym
        self.stack = []
        self.ss_stack = []
        self.gen_code = ''
        self.output = output

        self.symbol_table = [[] for x in xrange(24)]
        self.scope_num = 0
        self.temp_count = 0

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
        print "Symbol Table:"
        print self.symbol_table
        print '-' * 80

    def _call_action(self, X):
        action = X.split('#')[1].lower()
        eval("self." + action)


    def ll_compiler(self):
        token_text, a = self.scanner.scan()

        # push start symbol on both stacks
        self.stack.append(self.start_sym)
        self.ss_stack.append(self.start_sym)
        self.left_idx = 0
        self.right_idx = 0
        self.current_idx = 0
        self.top_idx = 1

        # now we start our loop
        while self.stack:
            X = self.stack[-1]


            if a == 'EmptySpace' or a == 'Comment':
                token_text, a = self.scanner.scan()
                continue

            if X == 'lambda':
                self.stack.pop()
                continue

            self._display_compile((self.left_idx, self.right_idx, self.current_idx, self.top_idx))
            # X is a non-terminal we have to process it
            if X in self.pg.ga.get_non_terminals():
                col = self.rev_tk_mapping[a]
                col_num = self.pg.col_matching[col]

                self.stack.pop()
                # Push EOP, a tuple in this case, on to the parse stack
                self.stack.append((self.left_idx, self.right_idx, self.current_idx, self.top_idx))

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
                            raise SyntaxError(a)

                for x in new_X[::-1]:
                    # only push non action symbols on the SS stack
                    if '#' not in x:
                        self.ss_stack.append(x)
                    # Push everything on the Parse stack
                    self.stack.append(x)

                self.left_idx = self.current_idx
                self.right_idx = self.top_idx
                self.current_idx = self.right_idx
                self.top_idx = self.top_idx + (len(new_X) - 1)



            # X is terminal
            elif X in self.pg.ga.get_terminals():
                if X == self.rev_tk_mapping[a]:

                    if token_text.isdigit():
                        self.ss_stack[self.current_idx] = sem_rec(token_text)
                    else:
                        self.ss_stack[self.current_idx] = sem_rec(token_text)

                    self.stack.pop()
                    token_text, a = self.scanner.scan()
                    self.current_idx += 1
                else:
                    raise SyntaxError(a)

            # X is EOP
            elif type(X) == tuple:
                self.left_idx = X[0]
                self.right_idx = X[1]
                self.current_idx = X[2]
                self.top_idx = X[3]

                self.current_idx += 1

                self.stack.pop()

            # X is action symbol
            else:
                self.stack.pop()
                self._call_action(X)

        #finally write to a file
        with open(self.output, 'w') as f:
            f.write(self.gen_code)


    # All of the semantic routine start here
    def start(self):
        pass

    def begin(self):
        self.scope_num += 1
        self.generate("BEGIN\n")

    def end(self):
        for l in self.symbol_table:
            for sym, scope in l:
                if scope == self.scope_num:
                    l.pop()
        self.scope_num -= 1
        self.generate("END\n")

    def assign(self, target, source):
        self.generate("STORE", 
                      self.extract_sem(self.ss_stack[self.right_idx + source]),
                      self.extract_sem(self.ss_stack[self.right_idx + target]))

    def read_id(self, invar):
        self.generate("READ", self.extract_sem(self.ss_stack[self.right_idx + invar]), "Integer")

    def write_expr(self, e):
        self.generate("WRITE",
                      self.extract_sem(self.ss_stack[self.right_idx + e]),
                      "Integer")

    def gen_infix(self, op, e):
        sr = sem_rec(self.get_temp())
        self.generate(self.extract_sem(self.ss_stack[self.right_idx + op]),
                      self.extract_sem(self.ss_stack[self.left_idx]),
                      self.extract_sem(self.ss_stack[self.right_idx + e]),
                      self.extract_sem(sr))
        self.ss_stack[self.left_idx] = sr

    def process_id(self):
        self.check_id(self.extract_sem(self.ss_stack[self.current_idx - 1]))
        self.ss_stack[self.left_idx] = sem_rec(self.extract_sem(self.ss_stack[self.current_idx - 1]))

    def process_literal(self):
        self.check_id(self.extract_sem(self.ss_stack[self.current_idx - 1]))
        self.ss_stack[self.left_idx] = self.ss_stack[self.current_idx - 1]

    def process_op(self):
        self.ss_stack[self.left_idx] = self.ss_stack[self.current_idx -1]

    def copy(self, source, target):
        if target == -1:
            self.ss_stack[self.left_idx] = self.ss_stack[self.right_idx + source]
        else:
            self.ss_stack[self.right_idx + target] = self.ss_stack[self.right_idx + source]

    def finish(self):
        self.generate("HALT")

    # All of the aux routines
    def generate(self, s1, s2=None, s3=None, s4=None):
        if s4:
            self.gen_code += "%s %s, %s, %s\n" % (s1, s2, s3, s4)
        elif s3:
            self.gen_code += "%s %s, %s\n" % (s1, s2, s3)
        else:
            self.gen_code += "%s" % s1

    def extract_sem(self, rec):
        if type(rec) == ExprRec:
            return self.extract(rec)
        elif type(rec) == OpRec:
            return self.extract_op(rec)
        else:
            raise SyntaxError

    def extract(self, e):
        return e.val

    def extract_op(self, o):
        if o.op == "+":
            return "ADD"
        else:
            return "SUB"

    def look_up(self, s):
        for l in self.symbol_table:
            try:
                if l[-1] == (s, self.scope_num):
                    return True
            except IndexError:
                continue
        return False

    def enter(self, s):
        idx = self.hash_entry(s)
        entry = self.symbol_table[idx]
        entry.append((s, self.scope_num))

    def check_id(self, s):
        if not self.look_up(s):
            self.enter(s)
            self.generate("DECLARE", s, "Integer")

    def get_temp(self):
        self.temp_count += 1
        return "Temp&%s" % self.temp_count

        temp_name = "Temp&%s" % max_temp
        check_id(temp_name)
        return temp_name

    def hash_entry(self, s):
        if type(s) == int:
            return s % 24
        s = s.lower()
        sum = 0
        for c in s:
            if c.isdigit():
                sum += ord(c) - 48
            else:
                sum += ord(c) - 96

        return sum % 24
