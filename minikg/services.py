from types import SimpleNamespace

from minikg.llm import LlmApi


class Services(SimpleNamespace):
    llm_api = LlmApi()
    pass


services = Services()
