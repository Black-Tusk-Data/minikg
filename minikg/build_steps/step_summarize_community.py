from expert_llm.models import ChatBlock
from expert_llm.remote.openai_shaped_client_implementations import OpenAIApiClient

from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.graph_merger import GraphMerger
from minikg.models import MiniKgConfig
from minikg.build_output import BuildStepOutput_Graph, BuildStepOutput_MultiGraph, BuildStepOutput_Text


# could be useful
class Step_SummarizeCommunity(MiniKgBuilderStep[BuildStepOutput_Text]):
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        graph: BuildStepOutput_Graph,
        community_name: str,
        community: list[str],
    ) -> None:
        super().__init__(config)
        self.graph = graph
        self.community = community
        self.community_name = community_name
        self.llm_client = OpenAIApiClient("gpt-4o")
        return

    def get_id(self) -> str:
        return f"community-summary:{self.community_name}"

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Text

    def _execute(self) -> BuildStepOutput_Text:
        nodes = self.graph.G.subgraph(self.community)
        summary = self.llm_client.chat_completion([
            ChatBlock(role="system", content=f"You are a {self.config.knowledge_domain} expert."),
            # TODO: prompt
        ]).content
        return BuildStepOutput_Text(text=summary)

    pass
