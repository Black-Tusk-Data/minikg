from expert_llm.models import ChatBlock
from expert_llm.remote.openai_shaped_client_implementations import OpenAIApiClient

from minikg.models import LlmResponse


class LlmApi:
    def __init__(self, model: str):
        self.llm_client = OpenAIApiClient(model)
        return

    def completion(
        self,
        *,
        req_name: str,
        system: str,
        user: str,
        output_schema: dict | None = None,
        max_tokens: int = 16000,
    ) -> LlmResponse:
        # can persist the requests if you want to keep track of them
        chat_blocks = [
            ChatBlock(
                role="system",
                content=system,
            ),
            ChatBlock(
                role="user",
                content=user,
            ),
        ]
        result: LlmResponse
        if output_schema:
            output = self.llm_client.structured_completion_raw(
                chat_blocks=chat_blocks,
                output_schema=output_schema,
                max_tokens=max_tokens,
            )
            result = LlmResponse(
                structured_output=output,
            )
            pass
        else:
            completion = self.llm_client.chat_completion(
                chat_blocks, max_tokens=max_tokens
            )
            result = LlmResponse(message=completion.content)
            pass
        return result

    pass
