from fnmatch import fnmatch
import os
from pathlib import Path

from minikg.models import MiniKgConfig


def get_all_input_files(config: MiniKgConfig) -> list[Path]:
    # this could be its own step, where we check with the LLM if it's a code file or not
    ignore_expressions = [
        "**/.git",
        *(config.ignore_expressions or []),
    ]
    potential_paths = set(
        Path(
            os.path.relpath(
                path,
                config.input_dir,
            )
        )
        for exp in config.input_file_exps
        for path in config.input_dir.rglob(exp)
        if path.is_file()
    )

    return [
        path
        for path in potential_paths
        if not any(fnmatch(str(path), expr) for expr in ignore_expressions)
    ]
