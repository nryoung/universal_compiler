universal_compiler
==================

Requirements
------------
- Python version 2.7+


Test Grammar Analyzer:
----------------------

`$ python test_compiler.py grammar <file with productions>`

- Where the `<file with productions>` is the path to the file containing micro language productions.
- Example test files can be found in the `ext` dir.
- Prints out list of scanned tokens to stdout in a list.

Example test Grammar Analyzer command:
--------------------------------------

`$ python test_compiler.py grammar ext/test_grammar1`


Test Scanner:
-------------

`$ python test_compiler.py scanner <file with micro_lang>`

- Where the `<file with micro_lang>` is the path to the file containing micro language.
- Example test files can be found in the `ext` dir.
- Prints out list of scanned tokens to stdout in a list.

Example test Scanner command:
-----------------------------

`$ python test_compiler.py scanner ext/test_scanner1`
