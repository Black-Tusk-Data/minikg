from pathlib import Path
from typing import NamedTuple

from pydantic import BaseModel


class MiniKgConfig(NamedTuple):
    persist_dir: Path
    max_chunk_lines: int
    chunk_overlap_lines: int

    # def get_
    pass


class FileFragment(BaseModel):
    fragment_id: str
    source_path: Path
    start_line_incl: int
    end_line_excl: int
    pass
