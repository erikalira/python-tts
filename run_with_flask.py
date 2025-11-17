"""Wrapper runner at project root for Render and other hosts.

Render start commands often run from the repository root. This file executes
the module `src.run_with_flask` so `python run_with_flask.py` works when the
service command is configured at the project root.
"""
import runpy


if __name__ == '__main__':
    # execute the module as a script so its '__main__' block runs
    runpy.run_module('src.run_with_flask', run_name='__main__')
