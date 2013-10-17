universal_compiler
==================

Requirements
------------
- Python version 2.7+


Test Predict Table Generator:
-----------------------------

`$ python test_compiler.py table_generate <file with productions> --start_sym=<start symbol>`

- Where the `<file with productions>` is the path to the file containing micro language productions.
- Example test files can be found in the `ext` dir.
- If `--start_sym` is not specified it will default to `<system_goal>`
- Prints out Predict Table as derived from the Predict and Follow sets found earlier.
- NOTE: you may want to pipe the output of this command to `less`

Example test Predict Table Generator command:
---------------------------------------------

`$ python test_compiler.py table_generate ext/test_table_gen --start_sym='<system_goal>'`


Test Predict Generator:
-----------------------

`$ python test_compiler.py predict <file with productions> --start_sym=<start symbol>`

- Where the `<file with productions>` is the path to the file containing micro language productions.
- Example test files can be found in the `ext` dir.
- If `--start_sym` is not specified it will default to `<system_goal>`
- Prints out Derives Lambda, First Sets, Follow Sets, and Predict Sets for each production to std out.

Example test Predict Generator command:
---------------------------------------

`$ python test_compiler.py predict ext/test_predict2 --start_sym='<system_goal>'`


Test Grammar Analyzer:
----------------------

`$ python test_compiler.py grammar <file with productions>`

- Where the `<file with productions>` is the path to the file containing micro language productions.
- Example test files can be found in the `ext` dir.
- Prints out list of extracted production information to stdout in a list.

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
