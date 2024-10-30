from pathlib import Path

from minikg.models import MiniKgConfig


class Api:
    def __init__(
            self,
            *,
            config: MiniKgConfig,
    ):
        self.config = config
        return

    def build_fresh_kg(
            self,
            source_paths: list[Path],
    ) -> None:
        return

    def update_kg(
            self,
            source_paths: list[Path],
    ) -> None:
        return

    pass
