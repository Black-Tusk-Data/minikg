from types import SimpleNamespace

from expert_llm.remote.jina_ai_client import JinaAiClient

from minikg.llm import LlmApi


class Services(SimpleNamespace):
    embedding_api = JinaAiClient("jina-embeddings-v3")
    llm_api = LlmApi("gpt-4o")
    pass


services = Services()
