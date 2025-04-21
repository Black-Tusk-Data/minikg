from pathlib import Path
from minikg.models import FileFragment, MiniKgConfig


class Splitter:
    def __init__(
        self,
        *,
        config: MiniKgConfig,
    ):
        self.config = config
        self.window_offset = config.max_chunk_lines - config.chunk_overlap_lines
        return

    def split_file(self, path: Path) -> list[FileFragment]:
        fragments: list[FileFragment] = []
        sanitized_path = str(path).replace("/", "_")
        lines: list[str]
        with open(self.config.input_dir / path) as f:
            lines = f.readlines()
            pass

        lo, hi = 0, min([self.config.max_chunk_lines, len(lines)])
        while hi <= len(lines):
            fragments.append(
                FileFragment(
                    fragment_id=f"{sanitized_path}:{lo}-{hi}",
                    source_path=str(path),
                    start_line_incl=lo,
                    end_line_excl=hi,
                )
            )
            lo += self.window_offset
            hi += self.window_offset
            pass

        return fragments

    pass
