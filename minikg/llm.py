from expert_llm.models import ChatBlock
from expert_llm.remote.openai_shaped_client_implementations import OpenAIApiClient


class LlmApi:
    def __init__(self):
        self.llm_client = OpenAIApiClient("gpt-4o")
        return

    def completion(
            self,
            *,
            req_name: str,
            system: str,
            user: str,
    ) -> str:
        # can persist the requests if you want to keep track of them
        result = self.llm_client.chat_completion(
            [
                ChatBlock(
                    role="system",
                    content=system,
                ),
                ChatBlock(
                    role="user",
                    content=user,
                ),
            ]
        )
        return result.content
    pass
