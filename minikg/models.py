"""
 - Could include some few-shot examples
"""

import abc
import base64
import json
import pickle
from pathlib import Path
import re
from typing import Generic, Literal, NamedTuple, TypeVar

import networkx as nx
from pydantic import BaseModel, Field

from minikg.utils import scrub_title_key


GraphType = nx.Graph | nx.MultiGraph


class MiniKgConfig(NamedTuple):
    version: int

    knowledge_domain: str  # like 'sales calls'
    entity_types: list[str]

    persist_dir: Path
    input_dir: Path
    input_file_exp: str
    max_chunk_lines: int
    chunk_overlap_lines: int
    community_threshold_similarity: float = 0.5
    community_search_concurrency: int = 20
    community_algorithm: str = "louvain"
    document_desc: str = "document"
    index_graph: bool = True
    embedding_size: int = 1024
    embedding_model: str = "jina-embeddings-v3"
    max_relevant_communities: int = 10
    summary_prompts: dict[str, str] | None = None
    pass


class FileFragment(BaseModel):
    fragment_id: str
    source_path: str
    start_line_incl: int
    end_line_excl: int

    def read_contents(self) -> str:
        with open(self.source_path, "r") as f:
            lines = f.readlines()
            return "".join(lines[self.start_line_incl : self.end_line_excl])
        return

    pass


class CompletionShape(BaseModel):

    @classmethod
    def prompt_json_schema(cls: type["CompletionShape"]) -> dict:
        raw = cls.model_json_schema()
        return scrub_title_key(raw)

    pass


class Entity(CompletionShape):
    name: str = Field(description="Name of the entity")
    entity_type: str = Field(description="Type of entity")  # override as enum
    description: str = Field(description="A short description of the entity")
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


class Node(BaseModel):
    name: str
    entity_type: str
    description: str
    pass


class Edge(BaseModel):
    nodes: tuple[str, str]  # sorted order
    description: str
    edge_id: int = 0
    pass


class Community(BaseModel):
    child_node_ids: list[str] = Field(default_factory=list)
    child_community_ids: list[str] = Field(default_factory=list)
    id: str
    pass


# other
class GraphSearchResult(NamedTuple):
    nearest_member: float
    nodes: list[Node]
    edges: list[Edge]
    pass
