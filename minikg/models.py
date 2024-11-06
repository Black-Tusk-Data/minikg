"""
 - Could include some few-shot examples
"""

import abc
import base64
import json
import pickle
from pathlib import Path
import re
from typing import Literal, NamedTuple

import networkx as nx
from pydantic import BaseModel, Field

from minikg.utils import scrub_title_key


class MiniKgConfig(NamedTuple):
    knowledge_domain: str       # like 'sales calls'
    persist_dir: Path
    input_dir: Path
    input_file_exp: str
    max_chunk_lines: int
    chunk_overlap_lines: int
    pass


class FileFragment(BaseModel):
    fragment_id: str
    source_path: str
    start_line_incl: int
    end_line_excl: int

    def read_contents(self) -> str:
        with open(self.source_path, "r") as f:
            lines = f.readlines()
            return "".join(lines[
                self.start_line_incl:
                self.end_line_excl
            ])
        return
    pass


class MiniKgBuildPlanStepOutput(abc.ABC):
    @abc.abstractmethod
    def to_file(self, path: Path) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
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
        graph_bytes = pickle.dumps(
            self.G
        )
        json_data = json.dumps({
            "label": self.label,
            "graph_b64": base64.b64encode(
                graph_bytes
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

        graph_bytes = base64.b64decode(data["graph_b64"])
        return BuildStepOutput_Graph(
            G=pickle.loads(graph_bytes),
            label=data["label"],
        )

    pass


class BuildStepOutput_Chunks(MiniKgBuildPlanStepOutput):
    def __init__(
            self,
            *,
            chunks: list[FileFragment]
    ):
        self.chunks = chunks
        return

    def to_file(self, path: Path) -> None:
        with open(path, "w") as f:
            f.write(json.dumps({
                "chunks": [
                    chunk.model_dump()
                    for chunk in self.chunks
                ]
            }))
            pass
        return

    @staticmethod
    def from_file(path: Path) -> "BuildStepOutput_Chunks":
        data: dict
        with open(path, "r") as f:
            data = json.loads(f.read())
            chunks = [
                FileFragment.model_validate(chunk)
                for chunk in data["chunks"]
            ]
            return BuildStepOutput_Chunks(chunks=chunks)

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
    # this could definitely be a domain-specific enum!
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
