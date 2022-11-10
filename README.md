# static-code-analyzer
Python - CLI PEP8 Format Check

how to:
  1. pass .py file path or path of dir containing .py files as arg
  2. static_analyze.py will read file contents and look for PEP8 format errors
  3. any error(s) found are output to console 

single .py file
```console
unix@usr:~$ python src/static_analyze.py <foo_bar.py>
~\foo_bar.py Line 8: [S009] Function name 'getUser' should be written in snake_case
~\foo_bar.py Line 8: [S012] The default argument is mutable
~\foo_bar.py Line 15: [S001] Too long
~\foo_bar.py Line 18: [S007] Too many spaces after construction_name (def or class)
```

dir of .py files
```console
unix@usr:~$ python src/static_analyze.py <web-app/src>
~\web-app\src\__init__.py Line 1: [S004] At least two spaces required before inline comments
~\web-app\src\models.py Line 23: [S011] Variable name 'QUERYRESULTS' should be written in snake_case
~\web-app\src\models.py Line 23: [S012] Default argument is mutable
~\web-app\src\urls.py Line 4: [S002] Indentation is not a multiple of four
```
