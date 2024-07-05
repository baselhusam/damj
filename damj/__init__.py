"""
damj

This module provides the main class `Damj` for the `damj` package. The `Damj` class is designed to
help developers create prompts for large language models (LLMs) with ease by combining different
project files within the developer's working directory. The package supports various customization
options for including or excluding certain types of content from Python files and Jupyter
notebooks.

The `__all__` directive is used to specify the public interface of the module, which includes
the `Damj` class.

Classes:
    Damj: A class to generate prompts for LLMs by processing project files and applying
    customization options.

Usage example:
    ```python
    from damj import Damj

    damj = Damj(
        cwd='/path/to/project',
        whitelist_files=['*.py'],
        blacklist_files=['.venv', '__pycache__']
    )

    prompt = damj.project_info(
        project_overview="This is a sample project.",
        add_project_structure=True,
        add_files_content=True,
        py_options={'add_imports': True,
                    'add_comments': True,
                    'add_docstrings': False,
                    'ipynb_output': False}
    )

    prompt = damj.create_prompt(
        question="What is the purpose of this project?",
        copy_to_clipboard=True,
        to_markdown=False,
    )

    print(prompt)
    ```
"""
from damj.damj import Damj
__all__ = ['Damj']
