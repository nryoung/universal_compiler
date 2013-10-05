"""
Test runner for universal compiler implementation.
Depending on cmd line arguments it will run specific tests.
"""
import argparse

def test_predict(program):
    from compiler.predict_generator import PredictGenerator
    p = PredictGenerator(program)
    p.generate()

def test_grammar(program):
    from compiler.grammar_analyzer import GrammarAnalyzer
    g = GrammarAnalyzer(program)
    g.analyze()

def test_scanner(program):
    from compiler.compiler_errors import LexicalError
    from compiler.scanner import Scanner

    # Instantiate our Scanner and yield the token list
    token_list = []
    s = Scanner(program)
    try:
        while True:
            token = s.scan()
            if token:
                token_list.append(token)
            if token == 'EofSym':
                break
    except LexicalError as e:
        print "Lexical Error. Unknown character: '%s'" % e.err
    else:
        print token_list


if __name__ == '__main__':
    # Create cmd line object parser
    parser = argparse.ArgumentParser()
    parser.add_argument('test_type', type=str,
                        help="""The component of the compiler to be tested.
                             Options are: 'scanner' | 'parser' | 'unit' | 'compile' |
                                          'grammar' | 'predict'""")
    parser.add_argument('in_file', type=argparse.FileType('r'),
                        help='Name of the input file.')

    args = parser.parse_args()

    # Run the specific test depending on the args passed in
    if args.test_type == 'scanner':
        test_scanner(args.in_file)
    if args.test_type == 'grammar':
        test_grammar(args.in_file)
    if args.test_type == 'predict':
        test_predict(args.in_file)
    else:
        parser.print_help()
