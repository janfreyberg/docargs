import ast
from typing import Union


def is_private(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
) -> bool:
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


def find_init(node: ast.ClassDef):
    try:
        return next(
            method
            for method in node.body
            if isinstance(method, ast.FunctionDef)
            and method.name == "__init__"
        )
    except StopIteration:
        return None
