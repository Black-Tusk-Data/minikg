from expert_llm.models import ChatBlock
from expert_llm.remote.openai_shaped_client_implementations import OpenAIApiClient

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_merger import GraphMerger
from minikg.models import Community, MiniKgConfig
from minikg.build_output import (
    BuildStepOutput_BaseGraph,
    BuildStepOutput_CommunitySummary,
    BuildStepOutput_Graph,
)
from minikg.utils import get_prompt_context_lines_for_community_summary, get_prompt_context_lines_for_graph


class Step_SummarizeCommunity(MiniKgBuilderStep[BuildStepOutput_CommunitySummary]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        attribute_prompts: dict[str, str],
        community: Community,
        community_summaries: dict[str, BuildStepOutput_CommunitySummary],
        graph_output: BuildStepOutput_BaseGraph,
    ) -> None:
        super().__init__(config)
        self.attribute_prompts = attribute_prompts
        self.community = community
        self.community_summaries = community_summaries
        self.graph_output = graph_output
        self.llm_client = OpenAIApiClient("gpt-4o")
        return

    def get_id(self) -> str:
        return f"community-summary:{self.community.id}"

    @staticmethod
    def get_output_type():
        return BuildStepOutput_CommunitySummary

    def _execute(self) -> BuildStepOutput_CommunitySummary:
        subgraph = self.graph_output.G.subgraph(self.community.child_node_ids)
        prompt_context_lines: list[str] = get_prompt_context_lines_for_graph(subgraph)
        for community_id, summary_output in self.community_summaries.items():
            prompt_context_lines.extend(
                get_prompt_context_lines_for_community_summary(
                    community_id=community_id,
                    summary_output=summary_output,
                )
            )
            pass
        prompt_context = "\n".join(prompt_context_lines)

        summary_data: dict[str, str] = {}
        for name, prompt in self.attribute_prompts.items():
            result = self.llm_client.chat_completion(
                [
                    ChatBlock(
                        role="system",
                        content=" ".join ([
                            f"You are a {self.config.knowledge_domain} expert.",
                            "Your task is to extract information from a provided knowledge graph.",
                            "Refer ONLY to information from the knowledge graph in your responses.",
                            prompt,
                        ])
                    ),
                    ChatBlock(
                        role="user",
                        content=prompt_context,
                    )
                ]
            )
            summary_data[name] = result.content
            pass

        return BuildStepOutput_CommunitySummary(data=summary_data)

    pass
