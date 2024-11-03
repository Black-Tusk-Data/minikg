"""
 - Could include some few-shot examples
"""

import abc
import base64
import json
from pathlib import Path
from typing import Literal, NamedTuple

import networkx as nx
from pydantic import BaseModel, Field

from minikg.utils import scrub_title_key


class MiniKgConfig(NamedTuple):
    knowledge_domain: str       # like 'sales calls'
    persist_dir: Path
    max_chunk_lines: int
    chunk_overlap_lines: int
    pass


class MiniKgBuildPlanStepOutput(abc.ABC):
    @abc.abstractmethod
    def to_file(self, path: Path) -> None:
        pass

    @abc.abstractmethod
    @staticmethod
    def from_file(path: Path) -> "MiniKgBuildPlanStepOutput":
        pass
    pass


class BuildStepOutput_Graph(MiniKgBuildPlanStepOutput):
    def __init__(
            self,
            *,
            label: str,
            G: nx.Graph,
    ):
        self.label = label
        self.G = G
        return

    def to_file(self, path: Path) -> None:
        graph6_bytes = nx.to_graph6_bytes(self.G)
        json_data = json.dumps({
            "label": self.label,
            "graph6_b64": base64.b64encode(
                graph6_bytes
            ).decode("utf-8"),
        })
        with open(path, "w") as f:
            f.write(json_data)
            pass
        return

    @staticmethod
    def from_file(path: Path) -> "BuildStepOutput_Graph":
        data: dict
        with open(path, "r") as f:
            data = json.loads(f.read())
            pass

        graph6_bytes = base64.b64decode(
            data["graph6_b64"]
        )
        return BuildStepOutput_Graph(
            G=nx.from_graph6_bytes(graph6_bytes),
            label=data["label"],
        )

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
    source_entity: str = Field(
        description="Name of the source entity in the relationship",
    )
    target_entity: str = Field(
        description="Name of the target entity in the relationship",
    )
    relationship_description: str = Field(
        description="A description of why the source and target entities are related",
    )
    weight: int = Field(
        description="An integer score between 1 and 10 indicating the strength of the relationship between the source and target entities"
    )
    pass
