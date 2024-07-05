import os
from typing import List, Dict, Union
import pyperclip
from IPython.display import Markdown
from damj.utils import get_project_structure, matches_pattern, get_file_content, show_markdown

class Damj:
    def __init__(
        self,
        cwd: str,
        whitelist_files: List[str] = ["*"],
        blacklist_files: List[str] = [],
        snippet_marker: str = "```",
    ):
        self.cwd = cwd
        blacklist_files.extend([".venv", "__pycache__"]) # Add default blacklists
        self.blacklist_files = blacklist_files
        self.whitelist_files = self._get_whitelist_files(whitelist_files, blacklist_files)
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
            dirs[:] = [d for d in dirs if not d.startswith('.') and not matches_pattern(os.path.join(relative_root, d), blacklist_files)]

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
            py_options: Dict = {"add_imports": True,
                               "add_comments": True,
                               "add_docstrings": True,
                               "ipynb_output": True},
    ) -> str:

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

        prompt = self.prompt
        if question:
            prompt = self._add_question(prompt, question)

        prompt = self._post_process_prompt(prompt)

        if copy_to_clipboard:
            pyperclip.copy(prompt)

        if to_markdown:
            return show_markdown(prompt)

        return prompt
