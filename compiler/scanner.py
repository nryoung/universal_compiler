"""
Scanner implementation for universal compiler.
"""

from .compiler_errors import LexicalError


class Scanner(object):

    def __init__(self, micro_lang):
        self.micro_lang = str(micro_lang.read().rstrip('\n'))
        self.token_code = 0

        # This is ugly, this is tying implementation with definition
        # At some point this should be read in from a file
        self.transition_tbl = [
                                [ 1, 2, 3, 14, 4, ' ', 6, 17, 18, 19, 20, ' ', 3, 3, ' ', 22],
                                [ 1, 1, 11, 11, 11, 11, 11, 11, 11, 11, 11, 1, 11, 11, ' ', 22],
                                [12, 2, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, ' ', 22],
                                [13, 13, 3, 13, 13, 13, 13, 13, 13, 13, 13, 13, 3, 3, ' ', 22],
                                [21, 21, 21, 21, 5, 21, 21, 21, 21, 21, 21, ' ', 21, 21, ' ', 22],
                                [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 15, 5, 22],
                                [' ', ' ', ' ', ' ', ' ', 16, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 22]
                               ]

        # GARRR!!! this is even uglier. It is not clear but this mapping is supposed to be use with
        # the actions attribute below. We have to do this that way next_action() knows what to do next.
        # At some point this should be read in from a file
        self.action_tbl = [
                            [ 2, 2, 3, 4, 2, 1, 2, 4, 4, 4, 4, 1, 3, 3, 1, 6],
                            [ 2, 2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 2, 6, 6, 6, 6],
                            [ 6, 2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
                            [ 6, 6, 3, 6, 6, 6, 6, 6, 6, 6, 6, 6, 3, 3, 6, 6],
                            [ 6, 6, 6, 6, 2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
                            [ 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 2, 6],
                            [ 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 6]
                          ]

        self.actions = { 1: 'Error', 2: 'MoveAppend', 3: 'MoveNoAppend',
                         4: 'HaltAppend', 5: 'HaltNoAppend', 6: 'HaltReuse'
                       }

        self.char_mapping = {
                              ' ': 2, '+': 3, '-': 4, '=': 5, ':': 6, ',': 7, ';': 8,
                              '(': 9, ')': 10, '_': 11, '\t': 12, '\n': 13, '$': 15
                            }

        self.reserved_words = {
                               'BEGIN': 'BeginSym', 'END': 'EndSym',
                               'READ': 'ReadSym', 'WRITE': 'WriteSym' 
                              }

        self.tokens = {
                        11:'Id', 12:'IntLiteral', 13:'EmptySpace',
                        14:'PlusOp', 15:'Comment', 16:'AssignOp',
                        17:'Comma', 18:'SemiColon', 19:'LParen',
                        20:'RParen', 21: 'MinusOp', 22:'EofSym' 
                      }

    def current_char(self):
        return self.micro_lang[0]

    def consume_char(self):
        self.micro_lang = self.micro_lang[1:]

    def start_state(self):
        return 0

    def column(self, char):
        # first we check if alpha or digit
        if char.isalpha():
            return 0
        elif char.isdigit():
            return 1

        # now lookup the action we need
        try:
            col = self.char_mapping[char]
        except KeyError:
            # set column to other column
            col = 14

        return col


    def action(self, state, char):
        col = self.column(char)
        return self.actions[self.action_tbl[state][col]]

    def next_state(self, state, char):
        return self.transition_tbl[state][self.column(char)]

    def look_up(self, state, char):
        self.token_code = self.next_state(state, char)

    def check_exceptions(self, token_code, token_text):
        if token_text.upper() in self.reserved_words.keys():
            # we know this is a reserved word so we set the code
            # appropriately
            self.token_code = -1

    def scan(self, token_code=0, token_text=""):
        state = self.start_state()

        while True:
            action = self.action(state, self.current_char())

            if action == 'Error':
                raise LexicalError('ERROR')

            elif action == 'MoveAppend':
                state = self.next_state(state, self.current_char())
                token_text += self.current_char()
                self.consume_char()

            elif action =='MoveNoAppend':
                state = self.next_state(state, self.current_char())
                self.consume_char()

            elif action == 'HaltAppend':
                self.look_up(state, self.current_char())
                token_text += self.current_char()
                self.check_exceptions(self.token_code, token_text)
                self.consume_char()
                if self.token_code == 0:
                    self.scan(self.token_code, token_text)
                return (token_text, self.tokens[self.token_code])

            elif action == 'HaltNoAppend':
                self.look_up(state, self.current_char(), self.token_code)
                self.check_exceptions(self.token_code, token_text)
                self.consume_char()
                if self.token_code == 0:
                    self.scan(self.token_code, token_text)
                return (token_text, self.tokens[self.token_code])

            elif action == 'HaltReuse':
                self.look_up(state, self.current_char())
                self.check_exceptions(self.token_code, token_text)
                if self.token_code == 0:
                    self.scan(self.token_code, token_text)
                elif self.token_code == -1:
                    # return the reserved word symbol found
                    return (token_text, self.reserved_words[token_text])
                return (token_text, self.tokens[self.token_code])
