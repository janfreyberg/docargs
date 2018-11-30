import ast

from flake8 import utils as stdin_utils

from .check import check
from .version import version


class DocargsChecker:
    name = "flake8_docargs"
    version = version

    def __init__(self, tree: ast.AST, filename):
        """Create a DocargsChecker

        Parameters
        ----------
        tree : ast.AST
            The syntax tree to check.
        filename : str
            File name of source code.
        """

        self.tree = tree
        self.filename = filename

    def run(self):
        tree = self.tree
        if self.filename == "stdin":
            lines = stdin_utils.stdin_get_value()
            tree = ast.parse(lines)

        for statement, underdocumented, overdocumented in check(tree):
            for error in self.error(
                statement, underdocumented, overdocumented
            ):
                yield error

    def error(
        self,
        statement,
        underdocumented=None,
        overdocumented=None,
        line=None,
        column=None,
    ):
        """Produce an error for flake8.

        Parameters
        ----------
        statement : ast.AST
            The statement at which the error occurred.
        underdocumented : List[str], optional
            The list of Arguments that are not documented.
        overdocumented : List[str], optional
            The list of arguments that are over-documented.
        line : int, optional
            The line number.
        column : int, optional
            The column number.
        """

        line = line if line is not None else statement.lineno
        column = column if column is not None else statement.col_offset

        if underdocumented is not None and len(underdocumented) > 0:
            message = (
                "D001 "
                "These parameters are not "
                "documented: {}.".format(", ".join(underdocumented))
            )
            yield line, column, message, type(self)

        if overdocumented is not None and len(overdocumented) > 0:
            message = (
                "D002 "
                "Documented parameters not in the "
                "function signature: {}".format(", ".join(overdocumented))
            )
            yield line, column, message, type(self)
