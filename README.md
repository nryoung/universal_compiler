universal_compiler
==================

Requirements
------------
- Python version 2.7+


Test Scanner:
-------------

`$ python test_compiler.py scanner <file with micro_lang>`

- Where the `<file with micro_lang>` is the path to the file containing micro language.
- Example test files can be found in the `ext` dir.
- Prints out list of scanned tokens to stdout in a list.

Example test Scanner command:
-----------------------------

`$ python test_compiler.py scanner ext/test_scanner1`
