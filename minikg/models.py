"""
 - Could include some few-shot examples
"""

import abc
import base64
import json
import pickle
from pathlib import Path
import re
from typing import ClassVar, Generic, Literal, NamedTuple, TypeVar

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
    input_file_exps: list[str]
    max_chunk_lines: int
    chunk_overlap_lines: int
    # optional
    community_threshold_similarity: float = 0.5
    community_search_concurrency: int = 20
    community_algorithm: str = "louvain"
    document_desc: str = "document"
    entity_type_desc: str = ""
    entity_description_desc: str = ""
    entity_name_desc: str = ""
    extraction_entities_undirected: bool = True
    extraction_prompt_override_entity_head: str = ""
    extraction_prompt_override_entity_tail: str = ""
    extraction_prompt_override_entity_relationship_undirected: str = ""
    force_uppercase_node_names: bool = False
    group_cluster_size: int = 5
    ignore_expressions: list[str] | None = None
    index_graph: bool = True
    embedding_size: int = 1024
    embedding_model: str = "jina-embeddings-v3"
    max_concurrency: int = 4
    max_relevant_communities: int = 10
    max_step_attempts: int = 2
    role_desc: str = "an expert research assistant"
    summary_prompts: dict[str, str] | None = None
    s3_cache_bucket_name: str = ""
    s3_cache_bucket_prefix: str = ""
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
    def prompt_json_schema(
        cls: type["CompletionShape"],
        *,
        description_overrides: dict[str, str] | None = None,
    ) -> dict:
        raw = cls.model_json_schema()
        if description_overrides:
            for key, description in description_overrides.items():
                raw["properties"][key]["description"] = description
                pass
            pass
        return scrub_title_key(raw)

    pass


class Entity(CompletionShape):
    entity_type: str = Field(description="Type of entity")  # override as enum
    description: str = Field(description="A short description of the entity")
    name: str = Field(description="A unique name for the entity")
    pass


class EntityWithFragment(Entity):
    DELIMITER: ClassVar[str] = "::"

    fragment: FileFragment

    def get_qualified_name(self) -> str:
        return self.DELIMITER.join(
            [
                self.fragment.source_path,
                self.name,
            ]
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
    # weight: int = Field(
    #     description="An integer score between 1 and 10 indicating the strength of the relationship between the source and target entities",
    #     default=0,
    # )
    pass


class EntityRelationshipUndirected(CompletionShape):
    related_entities: list[str] = Field(
        description="IDs of related entities.  Only explicitly related entities should be included.",
    )
    relationship_description: str = Field(
        description="A description of why the identified entities are related",
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
    child_community_ids: list[str] = Field(default_factory=list)
    child_node_ids: list[str] = Field(default_factory=list)
    id: str
    pass


# other
class GraphSearchResult(NamedTuple):
    nearest_member: float
    nodes: list[Node]
    edges: list[Edge]
    pass


class Group(BaseModel):
    group_id: str
    child_community_ids: list[str]
    child_group_ids: list[str]
    summary: dict[str, str]
    pass
