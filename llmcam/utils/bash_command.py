"""Python module to execute bash commands with GPT Function calling. This is really risky to publish"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Utils/04_bash_command.ipynb.

# %% auto 0
__all__ = ['execute_bash_command']

# %% ../../nbs/Utils/04_bash_command.ipynb 4
import subprocess

# %% ../../nbs/Utils/04_bash_command.ipynb 5
def execute_bash_command(command: str) -> str:
    """Execute any given bash command with parameters"""
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return result
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.output}"
