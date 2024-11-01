from pathlib import Path
from typing import NamedTuple

from pydantic import BaseModel, Field

from minikg.utils import scrub_title_key


class MiniKgConfig(NamedTuple):
    knowledge_domain: str       # like 'sales calls'
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


class CompletionShape(BaseModel):

    @classmethod
    def prompt_json_schema(cls: type["CompletionShape"]) -> dict:
        raw = cls.model_json_schema()
        return scrub_title_key(raw)
    pass


class Entity(CompletionShape):
    name: str = Field(
        description="Name of the entity"
    )
    labels: list[str] = Field(
        description="Applicable labels"
    )
    description: str = Field(
        description="A short description of the entity"
    )
    pass


class EntityRelationship(CompletionShape):
    entity_a: str
    entity_b: str
    name: str
    weight: float
    pass
