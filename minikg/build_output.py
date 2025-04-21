import abc
import base64
import json
import pickle
from pathlib import Path
import re
from typing import Generic, Literal, NamedTuple, TypeVar

import networkx as nx
from pydantic import BaseModel, Field

from minikg.models import (
    Entity,
    EntityRelationship,
    EntityWithFragment,
    FileFragment,
    GraphType,
    Community,
    Group,
)
from minikg.utils import scrub_title_key

GT = TypeVar("GT", bound=GraphType)


class MiniKgBuildPlanStepOutput(abc.ABC):
    @abc.abstractmethod
    def to_bytes(self) -> bytes:
        pass

    @classmethod
    @abc.abstractmethod
    def from_bytes(cls, raw: bytes) -> "MiniKgBuildPlanStepOutput":
        pass

    pass


class BuildStepOutput_BaseGraph(MiniKgBuildPlanStepOutput, Generic[GT], abc.ABC):
    def __init__(
        self,
        *,
        label: str,
        G: GT,
    ):
        self.label = label
        self.G = G
        return

    def to_bytes(self) -> bytes:
        graph_bytes = pickle.dumps(self.G)
        json_data = json.dumps(
            {
                "label": self.label,
                "graph_b64": base64.b64encode(graph_bytes).decode("utf-8"),
            }
        )
        return json_data.encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "BuildStepOutput_BaseGraph":
        data = json.loads(raw)
        graph_bytes = base64.b64decode(data["graph_b64"])
        graph = pickle.loads(graph_bytes)
        return cls(
            G=graph,
            label=data["label"],
        )

    pass


class BuildStepOutput_Graph(BuildStepOutput_BaseGraph[nx.Graph]):
    pass


class BuildStepOutput_MultiGraph(BuildStepOutput_BaseGraph[nx.MultiGraph]):
    pass


class BuildStepOutput_Chunks(MiniKgBuildPlanStepOutput):
    def __init__(self, *, chunks: list[FileFragment]):
        self.chunks = chunks
        return

    def to_bytes(self) -> bytes:
        dat = json.dumps({"chunks": [chunk.model_dump() for chunk in self.chunks]})
        return dat.encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "BuildStepOutput_Chunks":
        data = json.loads(raw)
        chunks = [FileFragment.model_validate(chunk) for chunk in data["chunks"]]
        return BuildStepOutput_Chunks(chunks=chunks)

    pass


class BuildStepOutput_Text(MiniKgBuildPlanStepOutput):
    def __init__(self, *, text: str):
        self.text = text
        return

    def to_bytes(self) -> bytes:
        return self.text.encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "BuildStepOutput_Text":
        return BuildStepOutput_Text(text=raw.decode("utf-8").strip())

    pass


class BuildStepOutput_CommunitySummary(MiniKgBuildPlanStepOutput):
    def __init__(
        self,
        *,
        data: dict[str, str],
    ):
        self.data = data
        return

    def to_bytes(self) -> bytes:
        return json.dumps(self.data).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "BuildStepOutput_CommunitySummary":
        return BuildStepOutput_CommunitySummary(data=json.loads(raw))

    pass


class BuildStepOutput_Groups(MiniKgBuildPlanStepOutput):
    def __init__(self, *, groups: list[Group]):
        self.groups = groups
        return

    def to_bytes(self) -> bytes:
        return json.dumps(
            {"groups": [group.model_dump() for group in self.groups]}
        ).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "BuildStepOutput_Groups":
        return BuildStepOutput_Groups(
            groups=[Group.model_validate(d) for d in json.loads(raw)["groups"]]
        )

    pass


# would like to wrap in an obj and add a 'name' to each community
class BuildStepOutput_Communities(MiniKgBuildPlanStepOutput):
    def __init__(self, communities: list[Community]):
        self.communities = communities
        return

    def to_bytes(self) -> bytes:
        return json.dumps([com.model_dump() for com in self.communities]).encode(
            "utf-8"
        )

    @classmethod
    def from_bytes(cls, raw: bytes) -> "BuildStepOutput_Communities":
        communities = [Community.model_validate(r) for r in json.loads(raw)]
        return cls(
            communities,
        )

    pass


class BuildStepOutput_Edges(MiniKgBuildPlanStepOutput):
    # Thinking about adding a 'problem files' member.
    def __init__(self, *, edges: list[EntityRelationship]):
        self.edges = edges
        return

    def to_bytes(self) -> bytes:
        return json.dumps({"edges": [edge.model_dump() for edge in self.edges]}).encode(
            "utf-8"
        )

    @classmethod
    def from_bytes(cls, raw: bytes) -> "BuildStepOutput_Edges":
        data = json.loads(raw)
        edges = [EntityRelationship.model_validate(entity) for entity in data["edges"]]
        return BuildStepOutput_Edges(edges=edges)

    pass


class BuildStepOutput_Entities(MiniKgBuildPlanStepOutput):
    def __init__(self, *, entities: list[EntityWithFragment]):
        self.entities = entities
        return

    def to_bytes(self) -> bytes:
        return json.dumps(
            {"entities": [entity.model_dump() for entity in self.entities]}
        ).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "BuildStepOutput_Entities":
        data = json.loads(raw)
        entities = [
            EntityWithFragment.model_validate(entity) for entity in data["entities"]
        ]
        return BuildStepOutput_Entities(
            entities=entities,
        )

    pass


class BuildStepOutput_Package(MiniKgBuildPlanStepOutput):
    def __init__(
        self,
        *,
        G: nx.MultiGraph,  # or just 'Graph'
        communities: dict[str, Community],
        community_db_names: list[str],
        community_hierarchy: list[list[str]],
        summaries_by_id: dict[str, dict[str, str]],
        cluster_groups: dict[str, Group],
    ):
        self.G = G
        self.communities = communities
        self.community_db_names = community_db_names
        self.community_hierarchy = community_hierarchy
        self.summaries_by_id = summaries_by_id
        self.cluster_groups = cluster_groups
        return

    def to_bytes(self) -> bytes:
        graph_bytes = pickle.dumps(self.G)
        dat = {
            "graph_b64": base64.b64encode(graph_bytes).decode("utf-8"),
            "communities": {
                key: com.model_dump() for key, com in self.communities.items()
            },
            "community_db_names": self.community_db_names,
            "community_hierarchy": self.community_hierarchy,
            "summaries_by_id": self.summaries_by_id,
            "cluster_groups": {
                key: group.model_dump() for key, group in self.cluster_groups.items()
            },
        }
        return json.dumps(dat).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "BuildStepOutput_Package":
        dat = json.loads(raw)
        graph_bytes = base64.b64decode(dat["graph_b64"])
        graph = pickle.loads(graph_bytes)
        return cls(
            G=graph,
            cluster_groups={
                key: Group.model_validate(r) for key, r in dat["cluster_groups"].items()
            },
            communities={
                key: Community.model_validate(r)
                for key, r in dat["communities"].items()
            },
            community_db_names=dat["community_db_names"],
            community_hierarchy=dat["community_hierarchy"],
            summaries_by_id=dat["summaries_by_id"],
        )

    pass
