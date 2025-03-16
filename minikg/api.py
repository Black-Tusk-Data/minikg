from collections import deque
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import logging
import os
from pathlib import Path
import re
from typing import Generic, TypeVar

from minikg.build_output import (
    BuildStepOutput_CommunitySummary,
    BuildStepOutput_Package,
    MiniKgBuildPlanStepOutput,
)
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.build_steps.step_compress_kg_edges import Step_CompressRedundantEdges
from minikg.build_steps.step_define_communities import Step_DefineCommunities
from minikg.build_steps.step_extract_chunk_kg import Step_ExtractChunkKg
from minikg.build_steps.step_index_community import Step_IndexCommunity
from minikg.build_steps.step_merge_kgs import Step_MergeKgs
from minikg.build_steps.step_package import Step_Package
from minikg.build_steps.step_split_doc import Step_SplitDoc
from minikg.build_steps.step_summarize_community import Step_SummarizeCommunity
from minikg.graph_edge_compressor import GraphEdgeCompressor
from minikg.graph_semantic_db import GraphSemanticDb
from minikg.graphtools.community_detection import (
    CommunityDetector,
    CommunityDetectorLeiden,
    CommunityDetectorLouvain,
)
from minikg.graphtools.community_summaries import get_community_summary_compute_order
from minikg.kg_searcher import KgCommunitiesSearcher
from minikg.models import Community, MiniKgConfig
from minikg.step_coordinators import STEP_COORDINATOR_ORDER
from minikg.step_coordinators.extract_chunk_level_kgs import (
    StepCoordinator_ExtractChunkLevelKgs,
)
from minikg.step_coordinators.merge_chunk_level_kgs import (
    StepCoordinator_MergeChunkLevelKgs,
)
from minikg.step_coordinators.split_docs import StepCoordinator_SplitDocs
from minikg.step_executor import StepExecutor


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
        self.executed_steps: dict[type[MiniKgBuilderStep], list[MiniKgBuilderStep]] = {}
        return

    def _load_package(self) -> BuildStepOutput_Package:
        return BuildStepOutput_Package.from_file(
            # bit hackish this handover here...
            self.config.persist_dir
            / "Step_Package"
            / str(self.config.version)
        )

    def build_kg(self) -> None:
        step_coordinators = [
            coordinator(self.config) for coordinator in STEP_COORDINATOR_ORDER
        ]
        self.executor.run_all_coordinators(step_coordinators)

        # # generally useful
        # master_graph_output = compress_step.output

        # kind of generally useful
        communities_by_id: dict[str, Community] = {}
        for community in define_communities_step.output.communities:
            communities_by_id[community.id] = community
            pass

        # SUMMARIZE
        summaries_by_id: dict[str, BuildStepOutput_CommunitySummary] = {}
        if self.config.summary_prompts:
            summary_compute_order: list[list[str]] = (
                get_community_summary_compute_order(define_communities_step.output)
            )
            for stage in summary_compute_order:
                stage_summary_steps = [
                    Step_SummarizeCommunity(
                        self.config,
                        attribute_prompts=self.config.summary_prompts,
                        community=communities_by_id[community_id],
                        community_summaries=summaries_by_id,
                        graph_output=master_graph_output,
                    )
                    for community_id in stage
                ]
                stage_summary_steps = self.executor.execute_all(stage_summary_steps)
                for community_id, step in zip(stage, stage_summary_steps):
                    assert step.output
                    summaries_by_id[community_id] = step.output
                    pass
                pass
            pass
        # END SUMMARIZE

        # INDEX
        index_community_steps: list[Step_IndexCommunity] = []
        if self.config.index_graph:
            index_community_steps = [
                Step_IndexCommunity(
                    self.config,
                    master_graph=compress_step.output,
                    community=community,
                )
                for i, community in enumerate(
                    define_communities_step.output.communities
                )
            ]
            index_community_steps = self.executor.execute_all(index_community_steps)
            pass
        # END INDEX

        # wrap this all up in a way that's easy to load from disk
        assert all([step.output for step in index_community_steps])
        packge_step = self.executor.execute_all(
            [
                Step_Package(
                    self.config,
                    master_graph=compress_step.output,
                    communities=define_communities_step.output,
                    community_indexes=[
                        step.output for step in index_community_steps if step.output
                    ],
                )
            ]
        )[0]
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
