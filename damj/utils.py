import os
from typing import List
import json
import ast
import textwrap
from IPython.display import Markdown


def get_indent(level: int) -> str:
    return "|   " * level

def matches_pattern(file_path: str, patterns: List[str]) -> bool:
    for pattern in patterns:
        if pattern == "*":
            return True
        if pattern in file_path:
            return True
    return False

def get_project_structure(cwd: str, blacklist_files: List[str]) -> str:

    project_structure_str = ""
    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not matches_pattern(os.path.join(root, d), blacklist_files)]

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
    with open(file_path, "r", encoding="utf-8") as file:
        notebook_content = json.load(file)
    
    result = ""
    add_comments = py_options.get("add_comments", True)
    add_imports = py_options.get("add_imports", True)
    add_docstrings = py_options.get("add_docstrings", True)
    include_output = py_options.get("ipynb_output", False)

    def process_code(code: str) -> str:
        if not add_docstrings:
            tree = ast.parse(code)
            tree = strip_docstrings(tree)
            code = ast.unparse(tree)

        if not add_comments:
            code = "\n".join(line for line in code.splitlines() if not line.strip().startswith("#"))

        if not add_imports:
            code = "\n".join(
                line for line in code.splitlines() if not line.strip().startswith("import") and not line.strip().startswith("from")
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
    if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        node.body = [n for n in node.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Str))]
    for child in ast.iter_child_nodes(node):
        strip_docstrings(child)
    return node


def get_file_content(file: str, py_options: dict) -> str:
    add_comments = py_options.get("add_comments", True)
    add_imports = py_options.get("add_imports", True)
    add_docstrings = py_options.get("add_docstrings", True)
    ipynb_output = py_options.get("ipynb_output", False)

    if file.endswith(".ipynb"):
        return handle_ipynb(file, py_options)

    with open(file, "r", encoding="latin-1") as f:
        new_code = f.read()

    if not add_comments:
        new_code = "\n".join(line for line in new_code.splitlines() if not line.strip().startswith("#"))

    if not add_imports:
        new_code = "\n".join(line for line in new_code.splitlines() if not line.strip().startswith("import") and not line.strip().startswith("from"))

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
