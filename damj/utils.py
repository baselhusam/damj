"""
Utility functions for the DAMJ package

This module provides utility functions for the DAMJ package, including functions to get
the project structure, get the content of a file, and convert text to markdown.
"""
import os
import ast
import json
import textwrap
from typing import List
from IPython.display import Markdown


def get_indent(level: int) -> str:
    """
    Get the indentation for a given level

    Parameters:
    ----------
    level : int
        The level of indentation

    Returns:
    -------
    str
        The indentation string
    """
    return "|   " * level

def matches_pattern(file_path: str, patterns: List[str]) -> bool:
    """
    Check if a file path matches any of the patterns

    Parameters:
    ----------
    file_path : str
        The file path to check
    patterns : List[str]
        The list of patterns to match

    Returns:
    -------
    bool
        True if the file path matches any of the patterns, False otherwise
    """
    for pattern in patterns:
        if pattern == "*":
            return True
        if pattern in file_path:
            return True
    return False

def get_project_structure(cwd: str, blacklist_files: List[str]=None) -> str:
    """
    Get the project structure

    Parameters:
    ----------
    cwd : str
        The current working directory
    blacklist_files : List[str]
        The list of files to exclude

    Returns:
    -------
    str
        The project structure
    """
    project_structure_str = ""
    if blacklist_files is None:
        blacklist_files = []
    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs
                   if not d.startswith('.')
                   and not matches_pattern(os.path.join(root, d), blacklist_files)]

        current_dir = os.path.relpath(root, cwd)
        indent_level = current_dir.count(os.sep)
        indent = get_indent(indent_level)

        if current_dir != ".":
            project_structure_str += f"{indent}├── {os.path.basename(root)}/\n"

        files.sort()

        for file in files:
            if file.startswith('.'):
                continue
            if matches_pattern(os.path.join(current_dir, file), blacklist_files):
                continue
            file_indent = get_indent(indent_level + 1)
            project_structure_str += f"{file_indent}├── {file}\n"

    return project_structure_str

def handle_ipynb(file_path: str, py_options: dict) -> str:
    """
    Handle Jupyter notebooks content

    Parameters:
    ----------
    file_path : str
        The file path of the Jupyter notebook
    py_options : dict
        The Python options
        The options include:
            - add_comments: bool
                Whether to include comments in the code
            - add_imports: bool
                Whether to include imports in the code
            - add_docstrings: bool
                Whether to include docstrings in the code
            - ipynb_output: bool
                Whether to include the output of the Jupyter notebook

    Returns:
    -------
    str
        The processed code
    """
    with open(file_path, "r", encoding="utf-8") as file:
        notebook_content = json.load(file)

    result = ""
    add_comments = py_options.get("add_comments", True)
    add_imports = py_options.get("add_imports", True)
    add_docstrings = py_options.get("add_docstrings", True)
    include_output = py_options.get("ipynb_output", False)

    def process_code(code: str) -> str:
        """
        Process the code

        Parameters:
        ----------
        code : str
            The code to process

        Returns:
        -------
        str
            The processed code
        """
        if not add_docstrings:
            tree = ast.parse(code)
            tree = strip_docstrings(tree)
            code = ast.unparse(tree)

        if not add_comments:
            code = "\n".join(line for line in code.splitlines()
                             if not line.strip().startswith("#"))

        if not add_imports:
            code = "\n".join(
                line for line in code.splitlines()
                if not line.strip().startswith("import")
                and not line.strip().startswith("from")
            )

        return code

    for cell in notebook_content.get("cells", []):
        if cell.get("cell_type") == "code":
            cell_code = "".join(cell.get("source", []))
            processed_code = process_code(cell_code)
            result += processed_code + "\n"
            if include_output:
                for output in cell.get("outputs", []):
                    if "text" in output:
                        result += "".join(output["text"]) + "\n"
                    elif "data" in output and "text/plain" in output["data"]:
                        result += "".join(output["data"]["text/plain"]) + "\n"
    return result

def strip_docstrings(node: ast.AST) -> ast.AST:
    """
    Strip docstrings from the AST

    Parameters:
    ----------
    node : ast.AST
        The AST node

    Returns:
    -------
    ast.AST
        The AST node with docstrings stripped
    """
    if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        node.body = [n for n in node.body if not (isinstance(n, ast.Expr)
                                            and isinstance(n.value, ast.Str))]
    for child in ast.iter_child_nodes(node):
        strip_docstrings(child)
    return node


def get_file_content(file: str, py_options: dict) -> str:
    """
    Get the content of a file

    Parameters:
    ----------
    file : str
        The file path
    py_options : dict
        The Python options
        The options include:
            - add_comments: bool
                Whether to include comments in the code
            - add_imports: bool
                Whether to include imports in the code
            - add_docstrings: bool
                Whether to include docstrings in the code

    Returns:
    -------
    str
        The content of the file
    """
    # GET OPTIONS
    add_comments = py_options.get("add_comments", True)
    add_imports = py_options.get("add_imports", True)
    add_docstrings = py_options.get("add_docstrings", True)

    # HANDLE JUPYTER NOTEBOOKS
    if file.endswith(".ipynb"):
        return handle_ipynb(file, py_options)

    # READ FILE
    with open(file, "r", encoding="latin-1") as file_code:
        new_code = file_code.read()

    # REMOVE COMMENTS
    if not add_comments:
        new_code = "\n".join(line for line in new_code.splitlines()
                             if not line.strip().startswith("#"))

    # REMOVE IMPORTS
    if not add_imports:
        new_code = "\n".join(line for line in new_code.splitlines()
                             if not line.strip().startswith("import")
                             and not line.strip().startswith("from"))

    # REMOVE DOCSTRINGS
    if not add_docstrings:
        tree = ast.parse(new_code)
        new_code = ast.unparse(strip_docstrings(tree))

    return new_code


def show_markdown(text: str) -> Markdown:
    """
    Convert text to markdown

    Parameters:
    ----------
    text : str
        The text to convert to markdown

    Returns:
    -------
    Markdown
        The markdown text
    """
    text = text.replace('•', '  *')
    text = text.replace('\n', '  \n')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
