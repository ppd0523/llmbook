from importlib.metadata import version

from rich.console import Console


Console().print(f"Python worktree ready (rich {version('rich')})")
