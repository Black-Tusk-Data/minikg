import hashlib
import logging

from sklearn.cluster import KMeans

from minikg.prompt_context import (
    get_prompt_context_lines_for_community_summary,
    get_prompt_context_lines_for_graph,
)
from minikg.services import services
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_merger import GraphMerger
from minikg.models import Community, Group, MiniKgConfig
from minikg.build_output import (
    BuildStepOutput_BaseGraph,
    BuildStepOutput_CommunitySummary,
    BuildStepOutput_Graph,
    BuildStepOutput_Groups,
)


class Step_ClusterGroups(MiniKgBuilderStep[BuildStepOutput_Groups]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        groups: list[Group],
        clustering_round: int,
    ) -> None:
        super().__init__(config)
        self.groups = groups
        self.clustering_round = clustering_round
        return

    def get_id(self) -> str:
        return f"clusters-round-{self.clustering_round}"

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Groups

    def _get_string_for_semantic_comparison(self, group: Group) -> str:
        return "\n".join(
            [
                "\n".join(
                    [
                        f"<{key.upper()}>",
                        value,
                        f"</{key.upper()}>",
                    ]
                )
                for key, value in group.summary.items()
            ]
        )

    def _cluster_embeddings(
        self,
        ids: list[str],
        embeddings: list[list[float]],
    ) -> list[list[str]]:
        n_clusters = max(len(self.groups) // self.config.group_cluster_size, 1)
        kmeans = KMeans(n_clusters=n_clusters)
        cluster_ids = kmeans.fit_predict(embeddings)
        clusters = [[] for _ in range(n_clusters)]
        for idx, cluster_id in enumerate(cluster_ids):
            clusters[cluster_id].append(ids[idx])
            pass
        return clusters

    def _summarize_clusters(
        self,
        *,
        clusters: list[list[str]],
        group_strings: dict[str, str],
    ) -> list[dict[str, str]]:
        assert self.config.summary_prompts
        summaries: list[dict[str, str]] = []
        for cluster in clusters:
            summary_data: dict[str, str] = {}
            for name, prompt in self.config.summary_prompts.items():
                summary = services.llm_api.completion(
                    req_name="summarize-group",
                    system=" ".join(
                        [
                            f"You are {self.config.role_desc}.",
                            "Refering ONLY to the provided context, respond to the following prompt:",
                            prompt,
                        ]
                    ),
                    user="\n\n".join(
                        [group_strings[cluster_id] for cluster_id in cluster]
                    ),
                )
                summary_data[name] = summary.message or ""
                pass
            summaries.append(summary_data)
            pass
        return summaries

    def _execute(self) -> BuildStepOutput_Groups:
        if not self.groups:
            return BuildStepOutput_Groups(
                groups=[],
            )

        group_strings = {
            group.group_id: self._get_string_for_semantic_comparison(group)
            for group in self.groups
        }
        group_embeddings = {
            group_id: embedding
            for group_id, embedding in zip(
                group_strings.keys(),
                services.embedding_api.embed(list(group_strings.values())),
            )
        }
        clusters = self._cluster_embeddings(
            ids=list(group_embeddings.keys()),
            embeddings=list(group_embeddings.values()),
        )
        logging.info(
            "clustered %d child groups into %d parent groups",
            len(self.groups),
            len(clusters),
        )
        # TODO: this should really be its own step
        cluster_summaries = self._summarize_clusters(
            clusters=clusters,
            group_strings=group_strings,
        )

        return BuildStepOutput_Groups(
            groups=[
                Group(
                    group_id=f"{self.clustering_round}-{i}",
                    # first round we're fed with the communities
                    child_group_ids=[] if self.clustering_round == 0 else clusters[i],
                    child_community_ids=(
                        clusters[i] if self.clustering_round == 0 else []
                    ),
                    summary=cluster_summaries[i],
                )
                for i in range(len(clusters))
            ]
        )

    pass
