"""
This module contains the `Damj` class, which is the main class for the `damj` package.
"""
import os
from typing import List, Dict, Union
from IPython.display import Markdown
import pyperclip
from damj.utils import get_project_structure, matches_pattern, get_file_content, show_markdown

class Damj:
    """
    Damj

    This class provides the main functionality for the `damj` package. The `Damj` class is
    designed to help developers create prompts for large language models (LLMs) with ease
    by combining different project files within the developer's working directory.

    The package supports various customization options for including or excluding certain
    types of content from Python files and Jupyter notebooks.

    You can read the Damj documentation on GitHub [HERE](https://github.com/baselhusam/damj).

    You can use the `Damj` class with the following methods:
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

    ---

    Also, you can have the following customization options:

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

    You can customize the `Damj` class by specifying the following parameters:
    - cwd: The current working directory
    - whitelist_files: A list of files to include in the prompt
    - blacklist_files: A list of files to exclude from the prompt
    - snippet_marker: The marker used to separate code snippets in the prompt

    Parameters:
    ----------
    cwd : str
        The current working directory
    whitelist_files : List[str], optional
        A list of files to include in the prompt, by default None
    blacklist_files : List[str], optional
        A list of files to exclude from the prompt, by default None
    snippet_marker : str, optional
        The marker used to separate code snippets in the prompt, by default "```"

    Attributes:
    ----------
    cwd : str
        The current working directory
    whitelist_files : List[str]
        A list of files to include in the prompt
    blacklist_files : List[str]
        A list of files to exclude from the prompt
    snippet_marker : str
        The marker used to separate code snippets in the prompt
    prompt : str
        The prompt generated by the `Damj` class

    Methods:
    --------

    ```python
    project_info(
        project_overview: str = "",
        add_project_structure: bool = False,
        add_files_content: bool = False,
        py_options: Union[Dict, None] = None,
    ) -> str:
    ```
        Generate the project information for the prompt

    ```python
    create_prompt(
        question: Union[str, None] = None,
        copy_to_clipboard: bool = True,
        to_markdown: bool = False,
    ) -> Union[str, Markdown]:
    ```
        Create the prompt for the large language model (LLM)
    """
    def __init__(
        self,
        cwd: str,
        whitelist_files: List[str] = None,
        blacklist_files: List[str] = None,
        snippet_marker: str = "```",
    ):
        self.cwd = cwd
        whitelist_files = ["*"] if whitelist_files is None else whitelist_files
        self.blacklist_files = ["__pycache__"] if blacklist_files is None else blacklist_files
        self.whitelist_files = self._get_whitelist_files(whitelist_files, self.blacklist_files)
        self.snippet_marker = snippet_marker
        self.prompt = ""


    def _get_whitelist_files(
        self,
        whitelist_files: List[str],
        blacklist_files: List[str]
    ) -> List[str]:

        matched_files = []

        for root, dirs, files in os.walk(self.cwd):
            relative_root = os.path.relpath(root, self.cwd)
            dirs[:] = [d for d in dirs if not d.startswith('.')
                       and not matches_pattern(os.path.join(relative_root, d), blacklist_files)]

            for file in files:
                file_path = os.path.join(relative_root, file)
                if file.startswith('.'):
                    continue

                if matches_pattern(file_path, blacklist_files):
                    continue
                if matches_pattern(file_path, whitelist_files):
                    matched_files.append(file_path)

        return matched_files

    def _add_project_overview(self, prompt: str, project_overview: str) -> str:
        prompt += f"""
# Project Overview
{project_overview}\n
"""
        return prompt

    def _add_project_structure(self, prompt: str, project_structure: str) -> str:
        prompt += f"""
# Project Structure
{project_structure}\n
"""
        return prompt

    def _get_relative_path(self, file: str) -> str:
        return os.path.relpath(os.path.join(self.cwd, file), self.cwd)

    def _add_file_content(self, prompt: str, file: str, file_content: str) -> str:
        relative_path = self._get_relative_path(file)
        prompt += f"""
{self.snippet_marker}{relative_path}
{file_content}
{self.snippet_marker}\n
"""
        return prompt

    def _add_files_content(self, prompt: str, py_options: Dict) -> str:
        for file in self.whitelist_files:
            file_content = get_file_content(file, py_options)
            prompt = self._add_file_content(prompt, file, file_content)
        return prompt

    def project_info(
            self,
            project_overview: str = "",
            add_project_structure: bool = False,
            add_files_content: bool = False,
            py_options: Union[Dict, None] = None,
    ) -> str:
        """
        Generate the project information for the prompt

        Parameters:
        ----------
        project_overview : str, optional
            The project overview, by default ""
        add_project_structure : bool, optional
            Whether to include the project structure in the prompt, by default False
        add_files_content : bool, optional
            Whether to include the content of the project files in the prompt, by default False
        py_options : Union[Dict, None], optional
            The Python options to customize the content of the Python files, by default None

        Returns:
        -------
        str
            The prompt generated by the `Damj` class
        """
        if py_options is None:
            py_options = {
                "add_comments": True,
                "add_imports": True,
                "add_docstrings": True,
                "ipynb_output": False
            }

        prompt = self.prompt
        if project_overview:
            prompt = self._add_project_overview(self.prompt, project_overview)

        if add_project_structure:
            project_structure_str = get_project_structure(self.cwd, self.blacklist_files)
            prompt = self._add_project_structure(prompt, project_structure_str)

        if add_files_content:
            prompt = self._add_files_content(prompt, py_options)

        self.prompt = prompt
        return prompt


    def _add_question(self, prompt: str, question: str) -> str:
        prompt += f"""
# Question
{question}\n
"""
        return prompt

    def _post_process_prompt(self, prompt: str) -> str:
        prompt = prompt.strip()
        return prompt

    def create_prompt(
        self,
        question: Union[str, None] = None,
        copy_to_clipboard: bool = True,
        to_markdown: bool = False,
    ) -> Union[str, Markdown]:
        """
        Create the prompt for the large language model (LLM)

        Parameters:
        ----------
        question : Union[str, None], optional
            The question to include in the prompt, by default None
        copy_to_clipboard : bool, optional
            Whether to copy the prompt to the clipboard, by default True
        to_markdown : bool, optional
            Whether to display the prompt as Markdown, by default False

        Returns:
        -------
        Union[str, Markdown]
            The prompt generated by the `Damj` class
        """
        prompt = self.prompt
        if question:
            prompt = self._add_question(prompt, question)

        prompt = self._post_process_prompt(prompt)

        if copy_to_clipboard:
            pyperclip.copy(prompt)

        if to_markdown:
            return show_markdown(prompt)

        return prompt
