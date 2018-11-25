import ast
from flake8 import utils as stdin_utils

from .check import check
from .version import version


class DocargsChecker:
    name = "flake8_docargs"
    version = version

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename

    def run(self):
        tree = self.tree
        if self.filename == "stdin":
            lines = stdin_utils.stdin_get_value()
            tree = ast.parse(lines)

        for statement, underocumented, overdocumented in check(tree):
            for error in self.error(statement, underocumented, overdocumented):
                yield error

    def error(
        self,
        statement,
        undocumented=None,
        overdocumented=None,
        line=None,
        column=None,
    ):

        line = line if line is not None else statement.lineno
        column = column if column is not None else statement.col_offset

        if undocumented is not None and len(undocumented) > 0:
            message = (
                "D001 "
                f"These parameters are not "
                f"documented: {', '.join(undocumented)}."
            )
            yield line, column, message, type(self)

        if overdocumented is not None and len(overdocumented) > 0:
            message = (
                "D002 "
                f"Documented parameters not in the "
                f"function signature: {', '.join(overdocumented)}"
            )
            yield line, column, message, type(self)
