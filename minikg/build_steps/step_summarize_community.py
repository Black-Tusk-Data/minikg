import logging
from minikg.prompt_context import (
    get_prompt_context_lines_for_community_summary,
    get_prompt_context_lines_for_graph,
)
from minikg.services import services
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_merger import GraphMerger
from minikg.models import Community, MiniKgConfig
from minikg.build_output import (
    BuildStepOutput_BaseGraph,
    BuildStepOutput_CommunitySummary,
    BuildStepOutput_Graph,
)


class Step_SummarizeCommunity(MiniKgBuilderStep[BuildStepOutput_CommunitySummary]):
    MAX_CHARS = 500_000

    def __init__(
        self,
        config: MiniKgConfig,
        *,
        community: Community,
        community_summaries: dict[str, BuildStepOutput_CommunitySummary],
        graph_output: BuildStepOutput_BaseGraph,
    ) -> None:
        super().__init__(config)
        self.community = community
        self.community_summaries = community_summaries
        self.graph_output = graph_output
        return

    def get_id(self) -> str:
        return f"community-summary:{self.community.id}"

    @staticmethod
    def get_output_type():
        return BuildStepOutput_CommunitySummary

    def _get_prompt_context_lines(self) -> list[str]:
        lines: list[str] = []
        if self.community.child_community_ids:
            for child_com_id in self.community.child_community_ids:
                lines.extend(
                    get_prompt_context_lines_for_community_summary(
                        community_id=child_com_id,
                        summary_output=self.community_summaries[child_com_id],
                    )
                )
                pass
            pass
        if self.community.child_node_ids:
            subgraph = self.graph_output.G.subgraph(self.community.child_node_ids)
            lines.extend(get_prompt_context_lines_for_graph(subgraph))
            pass

        return lines

    def _execute(self) -> BuildStepOutput_CommunitySummary:
        assert self.config.summary_prompts
        prompt_context_lines: list[str] = self._get_prompt_context_lines()
        prompt_context = "\n".join(prompt_context_lines)[: self.MAX_CHARS]

        summary_data: dict[str, str] = {}
        for name, prompt in self.config.summary_prompts.items():
            summary = services.llm_api.completion(
                req_name="summarize-community",
                system=" ".join(
                    [
                        f"You are {self.config.role_desc}.",
                        "Refering ONLY to the provided context, respond to the following prompt:",
                        prompt,
                    ]
                ),
                user=prompt_context,
            )
            summary_data[name] = summary.message or ""
            pass

        return BuildStepOutput_CommunitySummary(data=summary_data)

    pass
