from expert_llm.models import ChatBlock
from expert_llm.remote.openai_shaped_client_implementations import OpenAIApiClient

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_merger import GraphMerger
from minikg.models import Community, MiniKgConfig
from minikg.build_output import (
    BuildStepOutput_Dict,
    BuildStepOutput_Graph,
)
from minikg.utils import build_prompt_context_from_graph


class Step_SummarizeCommunity(MiniKgBuilderStep[BuildStepOutput_Dict]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        attribute_prompts: dict[str, str],
        community: Community,
        graph: BuildStepOutput_Graph,
    ) -> None:
        super().__init__(config)
        self.attribute_prompts = attribute_prompts
        self.community = community
        self.graph = graph
        self.llm_client = OpenAIApiClient("gpt-4o")
        return

    def get_id(self) -> str:
        return f"community-summary:{self.community.id}"

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Dict

    def _execute(self) -> BuildStepOutput_Dict:
        subgraph = self.graph.G.subgraph(self.community)
        prompt_context = build_prompt_context_from_graph
        # TODO iss-7: should have edge 'description' as well
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

        return BuildStepOutput_Dict(data=summary_data)

    pass
