import ast
from typing import Union, Optional


def is_private(node: Union[ast.AST]) -> bool:
    """Return whether or not the node is "private" (starts with an underscore)

    Parameters
    ----------
    node : Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
        The function

    Returns
    -------
    bool
    """

    return getattr(node, "name", "not a function")[0] == "_"


def find_init(node: ast.ClassDef) -> Optional[ast.FunctionDef]:
    """Find the init-method of a class.

    Parameters
    ----------
    node : ast.ClassDef
        The class

    Returns
    -------
    ast.FuncDef
        The init method.
    """

    try:
        return next(
            method
            for method in node.body
            if isinstance(method, ast.FunctionDef)
            and method.name == "__init__"
        )
    except StopIteration:
        return None
