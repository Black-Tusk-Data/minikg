import abc
from minikg.models import MiniKgConfig


class MiniKgBuilderStep(abc.ABC):
    def __init__(
            self,
            config: MiniKgConfig,
    ):
        self.config = config
        return

    @abc.abstractmethod
    def get_id(self) -> str:
        """
        A unique identifier for caching.
        """
        pass

    @abc.abstractmethod
    @staticmethod
    def load_from_raw(raw: bytes) -> "MiniKgBuilderStep":
        pass

    @abc.abstractmethod
    @staticmethod
    def dump_output_to_raw() -> bytes:
        pass

    pass
