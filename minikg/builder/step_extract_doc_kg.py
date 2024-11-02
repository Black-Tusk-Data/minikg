from pathlib import Path
from minikg.builder.base_step import MiniKgBuilderStep
from minikg.models import MiniKgConfig


class Step_ExtractDocKg(MiniKgBuilderStep[None]):
    def __init__(
            self,
            config: MiniKgConfig,
            doc_path: Path,
    ) -> None:
        super().__init__(config)
        self.doc_path = doc_path
        return

    def _execute(self):
        # - read file
        # - run the KG extractor on it
        # 
        return
    pass
