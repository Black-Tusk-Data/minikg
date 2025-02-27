from collections import deque
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import logging
import os
from pathlib import Path
import re
from typing import Generic, TypeVar

from minikg.build_output import BuildStepOutput_Package
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_compress_kg_edges import Step_CompressRedundantEdges
from minikg.build_steps.step_define_communities import Step_DefineCommunitiesLouvain
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_index_community import Step_IndexCommunity
from minikg.build_steps.step_merge_kgs import Step_MergeKgs
from minikg.build_steps.step_package import Step_Package
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.graph_edge_compressor import GraphEdgeCompressor
from minikg.graph_semantic_db import GraphSemanticDb
from minikg.kg_searcher import KgCommunitiesSearcher
from minikg.models import MiniKgConfig


DEBUG = bool(int(os.environ.get("DEBUG", 0)))
if DEBUG:
    logging.warning("EXECUTING IN DEBUG MODE")
    pass


T = TypeVar("T", bound=MiniKgBuilderStep)


def execute_step(step: T) -> T:
    step.execute()
    return step


class StepExecutor(Generic[T]):
    MAX_CONCURRENCY = 5  # arbitrary

    def __init__(
        self,
        config: MiniKgConfig,
    ):
        self.config = config
        return

    def execute_all(self, steps: list[T]) -> list[T]:
        if not steps:
            return []
        logging.debug(
            "executing %d steps of type %s",
            len(steps),
            steps[0].__class__.__name__,
        )
        if DEBUG:
            for step in steps:
                return [execute_step(step) for step in steps]
            pass
        with ProcessPoolExecutor(max_workers=self.MAX_CONCURRENCY) as ex:
            completed_steps = list(ex.map(execute_step, steps))
            return completed_steps
        pass


class Api:
    def __init__(
        self,
        *,
        config: MiniKgConfig,
    ):
        self.config = config
        self.executor = StepExecutor(config)
        for dirpath in [
            config.persist_dir,
        ]:
            if not dirpath.exists():
                os.makedirs(dirpath)
                pass
            pass
        return

    def _load_package(self) -> BuildStepOutput_Package:
        return BuildStepOutput_Package.from_file(
            # bit hackish this handover here...
            self.config.persist_dir
            / "Step_Package"
            / str(self.config.version)
        )

    def _gather_input_files(self) -> list[Path]:
        ignore_expressions = [re.compile(rf"{self.config.input_dir}/\.git/?")]
        return [
            path
            for path in self.config.input_dir.rglob(self.config.input_file_exp)
            if not any(expr.search(str(path)) for expr in ignore_expressions)
            and path.is_file()
        ]

    def build_kg(self) -> None:
        source_paths = self._gather_input_files()
        logging.info("found %d source files", len(source_paths))

        logging.info("splitting documents")
        # split docs
        split_doc_steps = [
            Step_SplitDoc(self.config, doc_path=doc_path) for doc_path in source_paths
        ]
        split_doc_steps = self.executor.execute_all(split_doc_steps)

        logging.info("extracting chunk-level knowledge graphs")
        extract_chunk_kg_steps = [
            Step_ExtractChunkKg(self.config, fragment=fragment)
            for split_doc in split_doc_steps
            for fragment in split_doc.output.chunks
        ][:1935]
        extract_chunk_kg_steps = self.executor.execute_all(extract_chunk_kg_steps)

        logging.info("merging knowledge graphs")
        graphs_to_merge = [
            step.output for step in extract_chunk_kg_steps if step.output  # for typing
        ]
        merge_step = Step_MergeKgs(
            self.config,
            graphs=graphs_to_merge,
        )
        merge_step = self.executor.execute_all([merge_step])[0]

        assert merge_step.output
        logging.info("compressing redundant knowledge graph edges")
        compress_step = Step_CompressRedundantEdges(
            self.config,
            graph=merge_step.output,
        )
        compress_step = self.executor.execute_all([compress_step])[0]

        assert compress_step.output
        logging.info("defining communities")
        community_step = Step_DefineCommunitiesLouvain(
            self.config,
            graph=compress_step.output,
        )
        community_step = self.executor.execute_all([community_step])[0]

        assert community_step.output
        index_community_steps: list[Step_IndexCommunity] = []
        if self.config.index_graph:
            index_community_steps = [
                Step_IndexCommunity(
                    self.config,
                    master_graph=compress_step.output,
                    community=community,
                    community_name=f"community-{i}",
                )
                for i, community in enumerate(community_step.output.communities)
            ]
            index_community_steps = self.executor.execute_all(index_community_steps)
            pass

        # wrap this all up in a way that's easy to load from disk
        assert all([step.output for step in index_community_steps])
        packge_step = self.executor.execute_all(
            [
                Step_Package(
                    self.config,
                    master_graph=compress_step.output,
                    communities=community_step.output,
                    community_indexes=[step.output for step in index_community_steps],
                    # TODO: iss-1
                    community_names=[
                        f"community-{i}"
                        for i in range(len(community_step.output.communities))
                    ],
                )
            ]
        )[0]

        print("DONE FOR NOW!")
        return

    def search_kg(self, query: str, k: int):
        package = self._load_package()
        # we are not taking advantage of the 'master_graph' at this time

        searcher = KgCommunitiesSearcher(
            self.config,
            community_names=package.community_db_names,
            community_graph_dbs=[
                GraphSemanticDb(self.config, name=name)
                for name in package.community_db_names
            ],
        )

        return searcher.answer(query, k=k)

    def visualize_kg(self):
        import pygraphviz as pgv

        package = self._load_package()
        outdir = Path("community-viz")
        os.system(f"rm -rf {outdir}")
        os.system(f"mkdir {outdir}")

        for community, community_name in zip(
            package.communities,
            package.community_names,
        ):
            subgraph = package.G.subgraph(community)

            G_viz = pgv.AGraph()
            for node in subgraph.nodes:
                G_viz.add_node(
                    node,
                    label="\n".join(
                        [
                            node,
                            package.G.nodes[node]["entity_type"],
                        ]
                    ),
                )
                pass
            for edge in subgraph.edges:
                G_viz.add_edge(
                    (edge[0], edge[1]),
                    label=package.G.edges[edge]["description"],
                )
                pass

            G_viz.draw(str(outdir / f"./{community_name}.png"), prog="dot")
            pass

        return

    # TODO
    def update_kg(
        self,
        source_paths: list[Path],
    ) -> None:
        return

    pass
