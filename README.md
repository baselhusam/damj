![background](https://raw.githubusercontent.com/baselhusam/damj/main/assets/background.png)

<p align="center">
  <img alt="Damj Logo" style="width: 200px; max-width: 100%; height: auto;" src="https://raw.githubusercontent.com/baselhusam/damj/main/assets/logo.png"/>
  <h1 align="center">✨ <b> Damj </b> ✨</h1>
  <p align="center"> <b> damj </b> is a tool for creating comprehensive prompts for language models by combining project files and applying custom processing options.
</p>

[![PyPI](https://img.shields.io/pypi/v/damj)](https://pypi.org/project/damj/)
<!-- [![Downloads](https://static.pepy.tech/badge/damj)](https://pepy.tech/project/damj) -->


## Introduction
`damj` is designed to help developers create effective prompts for large language models (LLMs) such as ChatGPT. By combining different project files and applying customizable processing options, `damj` simplifies the process of generating prompts tailored to specific project contexts.

## Features
- Combine multiple project files into a single prompt.
- Apply customizable processing options to include/exclude comments, imports, and docstrings for python scripts.
- Support for processing Jupyter notebooks and including cell outputs.
- Easy integration and usage within Python projects.

## Installation

### From PyPI
You can install the latest release from PyPI:
```sh
pip install damj
```

### From Source
```sh
git clone https://github.com/baselhusam/damj.git
cd damj
pip install .
```

## Usage

### Basic Example

```python
import os
from damj import Damj

cwd = os.getcwd()
damj = Damj(cwd)

damj.project_info(
    project_overview="This is a sample project.",
    add_project_structure=True,
)

prompt = damj.create_prompt(
    question="What is the purpose of this project?",
)

print(prompt)
```

Output:
```
# Project Overview
This is a sample project.


# Project Structure
|   ├── LICENSE
|   ├── README.md
|   ├── pyproject.toml
|   ├── requirements.txt
├── assets/
|   ├── background.png
|   ├── logo.png
├── damj/
|   ├── __init__.py
|   ├── damj.py
|   ├── utils.py



# Question
What is the purpose of this project?
```

### Another Detailed Exmaple
```python
import os
from damj import Damj

cwd = os.getcwd()

damj = Damj(
    cwd=cwd,
    whitelist_files=["*.py"],
    blacklist_files=[".venv", "__pycache__"],
    snippet_marker="```"
)

damj.project_info(
    project_overview="This is a sample project.",
    add_project_structure=True,
    add_files_content=True,
    py_options={
        "add_imports": True,
        "add_comments": True,
        "add_docstrings": False,
        "ipynb_output": False
    }
)

prompt = damj.create_prompt(
    question="What is the purpose of this project?",
    copy_to_clipboard=True,
    to_markdown=False
)

print(prompt)
```

### Use damj Utils Components
damj also provides several utility functions that can be used independently. These utilities include functions to get the project structure, get file content, and more.

#### Get Project Structure
The `get_project_structure` function generates a markdown representation of the directory structure, excluding blacklisted files and directories.

```python
from damj.utils import get_project_structure

# Get the project structure excluding .venv and __pycache__ directories
cwd = os.getcwd()
blacklist = [".venv", "__pycache__"]
project_structure = get_project_structure(cwd, blacklist)
print(project_structure)
```

#### Get File Content
The `get_file_content` function retrieves the content of a file, applying the specified `py_options`.

```python
from damj.utils import get_file_content

py_options = {
    "add_comments": True,
    "add_imports": True,
    "add_docstrings": False,
    "ipynb_output": False
}

# Get the content of a Python file with the specified options
file_content = get_file_content("example.py", py_options)
print(file_content)
```

<br>

## License
This project is licensed under the Apache Software License. See the LICENSE file for details.

<br>

## Contributors
Basel Mather (baselmathar@gmail.com)

<br>

## Contributing
Contributions are welcome! Please fork the repository and open a pull request with your changes.
