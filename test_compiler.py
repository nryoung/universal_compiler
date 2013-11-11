"""
Test runner for universal compiler implementation.
Depending on cmd line arguments it will run specific tests.
"""
import argparse
import traceback

def test_compile(program, grammar, start_sym):
    from compiler.parser import Parser

    try:
        p = Parser(program, grammar, start_sym)
        p.ll_compiler()
    except:
        print traceback.format_exc()

def test_parser_driver(program, grammar, start_sym):
    from compiler.parser import Parser

    p = Parser(program, grammar, start_sym)
    p.ll_driver()

def test_table_generate(program, start_sym):
    from compiler.predict_generator import PredictGenerator
    p = PredictGenerator(program)
    p.generate_predict_table(start_sym)
    # first create a our columns string
    columns = "                "
    for elem in p.predict_tbl[0][1:]:
        columns += "%8s" % elem

    rows = []
    for row in p.predict_tbl[1:]:
        s = "%s\t" % row[0]
        for elem in row[1:]:
            s += "%8s" % elem
        rows.append(s)

    print columns
    for r in rows:
        print r
        print "-" * 130

    print "Just in case the table above is not formatted correctly above here is a unformatted dump of the table:"
    for e in p.predict_tbl:
        print e

def test_predict(program, start_sym):
    from compiler.predict_generator import PredictGenerator
    p = PredictGenerator(program)
    p.generate(start_sym)

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
                        help="""The component of the compiler to be tested:
                             'scanner', 'parser', 'unit', 'compile', 'grammar',
                             'predict', 'table_generate', 'parser_driver', 'compile'""")
    parser.add_argument('in_file', type=argparse.FileType('r'),
                        help='Name of the input file.')

    parser.add_argument('--grammar', type=argparse.FileType('r'),
                        default='ext/test_grammar1',
                        help='File with grammar productions to be used.')

    parser.add_argument('--start_sym', type=str,
                        default='<system_goal>',
                        help='Name of start symbol for follow sets.')

    args = parser.parse_args()

    # Run the specific test depending on the args passed in
    if args.test_type == 'scanner':
        test_scanner(args.in_file)
    elif args.test_type == 'grammar':
        test_grammar(args.in_file)
    elif args.test_type == 'predict':
        test_predict(args.in_file, args.start_sym)
    elif args.test_type == 'table_generate':
        test_table_generate(args.in_file, args.start_sym)
    elif args.test_type == 'parser_driver':
        test_parser_driver(args.in_file, args.grammar, args.start_sym)
    elif args.test_type == 'compile':
        test_compile(args.in_file, args.grammar, args.start_sym)
    else:
        parser.print_help()
