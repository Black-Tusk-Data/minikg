import abc
import base64
import json
import pickle
from pathlib import Path
import re
from typing import Generic, Literal, NamedTuple, TypeVar

import networkx as nx
from pydantic import BaseModel, Field

from minikg.graph_semantic_db import GraphSemanticDb
from minikg.models import FileFragment, GraphType, Community
from minikg.utils import scrub_title_key


GT = TypeVar("GT", bound=GraphType)


class MiniKgBuildPlanStepOutput(abc.ABC):
    @abc.abstractmethod
    def to_file(self, path: Path) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def from_file(cls, path: Path) -> "MiniKgBuildPlanStepOutput":
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

    def to_file(self, path: Path) -> None:
        graph_bytes = pickle.dumps(self.G)
        json_data = json.dumps(
            {
                "label": self.label,
                "graph_b64": base64.b64encode(graph_bytes).decode("utf-8"),
            }
        )
        with open(path, "w") as f:
            f.write(json_data)
            pass
        return

    @classmethod
    def from_file(cls, path: Path) -> "BuildStepOutput_BaseGraph":
        data: dict
        with open(path, "r") as f:
            data = json.loads(f.read())
            pass

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

    def to_file(self, path: Path) -> None:
        with open(path, "w") as f:
            f.write(
                json.dumps({"chunks": [chunk.model_dump() for chunk in self.chunks]})
            )
            pass
        return

    @classmethod
    def from_file(cls, path: Path) -> "BuildStepOutput_Chunks":
        data: dict
        with open(path, "r") as f:
            data = json.loads(f.read())
            chunks = [FileFragment.model_validate(chunk) for chunk in data["chunks"]]
            return BuildStepOutput_Chunks(chunks=chunks)

    pass


class BuildStepOutput_Text(MiniKgBuildPlanStepOutput):
    def __init__(self, *, text: str):
        self.text = text
        return

    def to_file(self, path: Path) -> None:
        with open(path, "w") as f:
            f.write(self.text)
            pass
        return

    @classmethod
    def from_file(cls, path: Path) -> "BuildStepOutput_Text":
        data: dict
        with open(path, "r") as f:
            return BuildStepOutput_Text(text=f.read().strip())

    pass


class BuildStepOutput_Dict(MiniKgBuildPlanStepOutput):
    def __init__(
            self,
            *,
            data: dict
    ):
        self.data = data
        return

    def to_file(self, path: Path) -> None:
        with open(path, "w") as f:
            f.write(json.dumps(self.data))
            pass
        return

    @classmethod
    def from_file(cls, path: Path) -> "BuildStepOutput_Dict":
        data: dict
        with open(path, "r") as f:
            return BuildStepOutput_Dict(data=json.load(f))

    pass


# would like to wrap in an obj and add a 'name' to each community
class BuildStepOutput_Communities(MiniKgBuildPlanStepOutput):
    def __init__(self, communities: list[Community]):
        self.communities = communities
        return

    def to_file(self, path: Path) -> None:
        with open(path, "w") as f:
            f.write(json.dumps([
                com.model_dump()
                for com in self.communities
            ]))
            pass
        return

    @classmethod
    def from_file(cls, path: Path) -> "BuildStepOutput_Communities":
        communities: list[Community]
        with open(path, "r") as f:
            communities = [
                Community.model_validate(r)
                for r in json.load(f)
            ]
            pass
        return cls(
            communities,
        )

    pass


class BuildStepOutput_IndexedCommunity(MiniKgBuildPlanStepOutput):
    def __init__(
        self,
        *,
        semantic_db_name: str,
    ):
        self.semantic_db_name = semantic_db_name
        return

    def to_file(self, path: Path) -> None:
        with open(path, "w") as f:
            f.write(self.semantic_db_name)
            pass
        return

    @classmethod
    def from_file(cls, path: Path) -> "BuildStepOutput_IndexedCommunity":
        with open(path, "r") as f:
            name = f.read().strip()
            return cls(
                semantic_db_name=name,
            )
        pass

    pass


class BuildStepOutput_Vacuous(MiniKgBuildPlanStepOutput):
    def to_file(self, path: Path) -> None:
        return

    @classmethod
    def from_file(cls, path: Path) -> "BuildStepOutput_Vacuous":
        return cls()

    pass


class BuildStepOutput_Package(MiniKgBuildPlanStepOutput):
    def __init__(
        self,
        *,
        G: nx.MultiGraph,  # or just 'Graph'
        communities: list[Community],
        community_db_names: list[str],
    ):
        self.G = G
        self.communities = communities
        self.community_db_names = community_db_names
        return

    def to_file(self, path: Path) -> None:
        graph_bytes = pickle.dumps(self.G)
        dat = {
            "graph_b64": base64.b64encode(graph_bytes).decode("utf-8"),
            "communities": [com.model_dump() for com in self.communities],
            "community_db_names": self.community_db_names,
        }
        with open(path, "w") as f:
            json.dump(dat, f)
            pass
        return

    @classmethod
    def from_file(cls, path: Path) -> "BuildStepOutput_Package":
        with open(path, "r") as f:
            dat = json.load(f)
            graph_bytes = base64.b64decode(dat["graph_b64"])
            graph = pickle.loads(graph_bytes)
            return cls(
                G=graph,
                communities=[Community.model_validate(r) for r in dat["communities"]],
                community_db_names=dat["community_db_names"],
            )
        pass

    pass
