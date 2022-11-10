import re
import string
import ast
from itertools import count
import os
import sys

MAX_LINE = 79
ASCII_UPPER = set(string.ascii_uppercase)

arg = sys.argv

ERRORS = {
    'S001': 's001 Too Long',
    'S002': 's002 Indentation is not a multiple of four',
    'S003': 's003 Unnecessary semicolon',
    'S004': 's004 At least two spaces required before inline comments',
    'S005': 's005 TODO Found',
    'S006': 's006 More than two blank lines used before this line',
    'S007': 's007 Too many spaces after construction_name (def or class)',
    'S008': 's008 Class name class_name should be written in CamelCase',
    'S009': 's009 Function name function_name should be written in snake_case',
    'S010': 's010 Argument name arg_name should be written in snake_case',
    'S011': 's011 Variable var_name should be written in snake_case',
    'S012': 's012 The default argument value is mutable'
}

n = count()


def get_file(arg):
    def validate_path_type(path):

        if os.path.exists(path):

            if os.path.isfile(path):
                return 'python file' if is_py(path) else False

            if os.path.isdir(path):
                return 'dir'
        return False

    def is_py(file):
        return file.split('.')[-1] == 'py'

    def read_dir(dir):
        return [x for x in os.listdir(dir) if x.split('.')[-1] == 'py']

    if arg and len(arg) > 1:

        path_type = validate_path_type(arg[1])

        if path_type and path_type == 'python file':
            return arg[1]

        if path_type == 'dir':
            return read_dir(arg[1])
    return False


class PEP(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __blank__ = 0

    def __init__(self, line):

        super().__init__()

        errors = {
            'S001': bool(len(line) > MAX_LINE),
            'S002': bool((sum(1 for x in line if x == " " and '#' not in line) % 2 >= 2)),
            'S003': bool(";" in line and self.invalid_semicolon(line)),
            'S004': self._inline_comment_error(line),
            'S005': bool('TODO' in str(line).upper() and '#' in str(line)),
            'S006': bool(PEP.__blank__ > 3),
            'S007': self._func_construct_error_(str(line).rstrip())
        }

        if line != '\n':
            PEP.__blank__ = 0
        PEP.__blank__ += 1

        line_errors = [error_code for error_code, error in errors.items() if error]
        line_no = next(n)

        try:
            self[line_no].append(line_errors)
        except KeyError:
            self[line_no] = line_errors

    @staticmethod
    def invalid_semicolon(line):

        if ';' in str(line).upper():
            if int(str(line).index(';')) < int(len(str(line).strip())):
                return True
        return False


    @staticmethod
    def _inline_comment_error(value):
        if "#" in value:
            return bool(sum(1 for j in value.split(" ") if j == '') != 1)

    @staticmethod
    def _cls_construct_error(_class):
        _cls_pattern_ = "class\s.*?:"
        _cls_ = re.match(_cls_pattern_, _class)
        return

    @staticmethod
    def _func_construct_error_(_func):

        if str(_func).startswith('def') or str(_func).startswith('class'):
            return bool(sum(1 for j in _func.split(" ") if j == '') >= 1)


class Line(PEP):
    _number = 0

    def __init__(self, line):
        super().__init__(line)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self[item]


class AstParser(ast.NodeVisitor):

    def __init__(self):
        self.errors = dict()

    def visit_Name(self, node: ast.Name) -> any:

        if isinstance(node.ctx, ast.Store) and set(node.id).intersection(ASCII_UPPER) and str(node.id) != 'TODO':
            self.new_error(str(node.id), 'S011', int(node.lineno))
        else:
            pass

    def visit_List(self, node: ast.List) -> any:
        if node:
            for i in ast.walk(node):
                if isinstance(i, ast.List) and len(i.elts) == 0:
                    self.new_error(str(i.elts), "S012", i.lineno)
                    break
                else:
                    pass
        else:
            pass

    def visit_arg(self, node: ast.arg) -> any:
        if set(node.arg).intersection(ASCII_UPPER):
            self.new_error(str(node.arg), "S010", node.lineno)
        else:
            pass

    def visit_Constant(self, node) -> any:

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> any:

        if set(node.name).intersection(ASCII_UPPER):
            self.new_error(str(node.name), "S009", int(node.lineno))
        else:
            pass

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> any:
        _class_ = list(node.name)
        if not _class_[0] == _class_[0].upper() or "_" in _class_:
            self.new_error(str(node.name), "S008", int(node.lineno))
        else:
            pass
        self.generic_visit(node)

    def new_error(self, line_content: str, error_code: str, line_number: int):
        content = {
            'content': f'{str(line_content)}',
            'errors': [error_code]
        }

        try:
            self.errors[int(line_number)].append(content)
        except KeyError:
            self.errors[int(line_number)] = [content]


class File(Line):

    def __init__(self, file_name: str, lines: list, multi=False):
        super().__init__(self)
        self.file_name = file_name
        self.content = [Line(line) for line in lines]

        if multi:
            self.multi_err = []
            self()

    def class_def_errors(self, file_name):

        tree = ast.parse(open(file_name, mode='r').read())
        ast_parser = AstParser()
        ast_parser.visit(tree)
        errors = ast_parser.errors

        return errors

    def format_error_out(self, error, content, func_class=None):
        return error.replace(
            func_class, ' '.join(
                x.strip().replace(':', '') for x in content.split(' ')
            )
        )

    def print_error(self, **kwargs):

        line_n, errors = kwargs['line_n'], kwargs['error_code']

        for error in errors:
            if isinstance(error, dict):
                content, sub_errors = error['content'], error['errors']
                for sub_error in sub_errors:
                    error_msg = ERRORS[sub_error].replace(
                        'class_name',
                        content).replace(
                        'function_name',
                        content).replace(
                        'arg_name',
                        content).replace('var_name', content)
            else:
                error_msg = ERRORS[error]
            try:
                if kwargs['multi'] == True:
                    e_msg = f"{self.file_name}: line {line_n}: {error_msg}"
                    return e_msg
            except Exception:
                pass
            finally:
                print(f"{self.file_name}: line {line_n}: {error_msg}")

    def __call__(self, *args, **kwargs):

        ast_errors = self.class_def_errors(self.file_name)

        for line_no, error in ast_errors.items():
            for _error in self.content:
                try:
                    _error[line_no].extend(error)
                except KeyError:
                    pass

        try:
            errors = [j for n, j in enumerate(self.content) if len(j.get(n + 1)) >= 1]

            for error in errors:
                for line, error_msg in error.items():
                    self.print_error(line_n=line, error_code=error_msg)

        except TypeError:
            print(self.content)
            pass


def pep_errors(python_file, multi=False):
    global n
    if multi:
        m = []
        for f in python_file:
            # f_path = f"test{os.path}{f}"
            File(os.path.join("test/this_stage", f),
                         open(os.path.join("test/this_stage", f), mode='r').readlines(), multi=True)
            del n
            n = count()


    else:

        with open(python_file, mode='r') as f:
            file = File(python_file, f.readlines())
        f.close()
        file(multi=False)


if __name__ == "__main__":

    if get_file(arg):
        if isinstance(get_file(arg), list):
            pep_errors(sorted(get_file(arg)), multi=True)
        else:
            pep_errors(get_file(arg))
