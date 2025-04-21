from types import SimpleNamespace

from expert_llm.api import LlmApi
from expert_llm.remote.openai_shaped_client_implementations import (
    OpenAIApiClient,
)


# can open up a lot here to be configured!
class Services(SimpleNamespace):
    embedding_api = OpenAIApiClient(
        "text-embedding-3-small",
        rate_limit_window_seconds=60,
        rate_limit_requests=5000,
        lock_type="multiprocessing",
    )
    llm_api = LlmApi(
        OpenAIApiClient(
            "gpt-4o-mini",
            rate_limit_window_seconds=60,
            rate_limit_requests=5000,
            lock_type="multiprocessing",
        )
    )
    pass


services = Services()
