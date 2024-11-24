"""
A top-level query looks like:
 - ask each communitiy the question
 - take the combined answers from each community,
   and perform a final super 'answer'

Within a community, a query looks like:
 - cosine similarity on any relevant nodes or edges
 - can simply include all those in a RAG request,
   or could also take a whole meaningful subgraph
"""

import logging
from btdcore.utils import map_multithreaded
from expert_llm.models import ChatBlock
from expert_llm.remote.openai_shaped_client_implementations import OpenAIApiClient
from minikg.graph_semantic_db import GraphSemanticDb
from minikg.models import MiniKgConfig, Node, Edge, GraphSearchResult


def get_context(search_result: GraphSearchResult):
    node_descs = [f"{node.name}: {node.description}" for node in search_result.nodes]
    # just using the descs for now...
    edge_descs = [f"{edge.description}" for edge in search_result.edges]
    return "\n".join(
        [
            "KNOWN ENTITIES:",
            *node_descs,
            "KNOWN RELATIONSHIPS:",
            *edge_descs,
        ]
    )


class KgCommunitiesSearcher:
    def __init__(
        self,
        config: MiniKgConfig,
        *,
        community_names: list[str],
        community_graph_dbs: list[GraphSemanticDb],
    ):
        self.config = config
        self.community_names = community_names
        self.community_graph_dbs = community_graph_dbs
        self.llm_client = OpenAIApiClient("gpt-4o")
        self.threshold_distance = 1 - config.community_threshold_similarity
        return

    def search_community(
        self,
        idx: int,
        *,
        query: str,
        k: int,
    ) -> GraphSearchResult:
        db = self.community_graph_dbs[idx]
        node_distances, nodes = db.search_nodes(query, k=k)
        edge_distances, edges = db.search_edges(query, k=k)
        return GraphSearchResult(
            nodes=nodes,
            edges=edges,
            nearest_member=min([*node_distances, *edge_distances]),
        )

    def search(self, query: str, *, k: int) -> dict[str, GraphSearchResult]:
        community_results = map_multithreaded(
            lambda i: self.search_community(i, query=query, k=k),
            range(len(self.community_graph_dbs)),
            self.config.community_search_concurrency,
        )
        # we attempt to select only the most relevant communities
        community_results = list(
            sorted(community_results, key=lambda x: x.nearest_member)
        )
        relevant_communities = community_results[: self.config.max_relevant_communities]
        # TODO: could potentially also use the 'min similarity' to further restrict
        return {
            self.community_names[i]: result
            for i, result in enumerate(relevant_communities)
        }

    def check_answer_is_relevant(
            self,
            *,
            query: str,
            answer: str,
    ) -> bool:
        relevance_result = self.llm_client.structured_completion_raw(
            chat_blocks=[
                ChatBlock(
                    role="user",
                    content="\n".join(
                        [
                            (
                                "Does the following text passage help to answer the query"
                                f""" "{query}"?"""
                            ),
                            "TEXT PASSAGE:",
                            answer,
                        ]
                    ),
                ),
            ],
            output_schema={
                "type": "object",
                "required": ["is_useful"],
                "properties": {
                    "is_useful": {
                        "type": "boolean",
                        "description": "Whether or not the text passage is useful to answering the query.",
                    },
                },
            },
        )
        return relevance_result["is_useful"]

    def check_statement_is_grounded(
            self,
            *,
            statement: str,
            context: str,
    ) -> bool:
        grounded_result = self.llm_client.structured_completion_raw(
            chat_blocks=[
                ChatBlock(
                    role="user",
                    content="\n".join(
                        [
                            (
                                "Does the following statement rely COMPLETELY on information from the following text passage? "
                                f""" "{statement}"?"""
                            ),
                            "TEXT PASSAGE:",
                            context,
                        ]
                    ),
                ),
            ],
            output_schema={
                "type": "object",
                "required": ["completely_reliant"],
                "properties": {
                    "completely_reliant": {
                        "type": "boolean",
                        "description": "Whether or not the statement is completely reliant on information from the text passage.",
                    },
                },
            },
        )
        return grounded_result["completely_reliant"]

    def answer(self, query: str, k: int) -> dict[str, str]:
        """
        Returns [community_name] -> community_response,
        plus a 'FINAL' -> final response
        """
        community_search_results = self.search(query, k=k)
        logging.info(
            "retrieved results from %d relevant communities",
            len(community_search_results),
        )
        responses = {}
        for community_name, search_result in community_search_results.items():
            if not search_result:
                continue
            context = get_context(search_result)
            community_answer = self.llm_client.chat_completion(
                [
                    ChatBlock(
                        role="system",
                        content=" ".join(
                            [
                                f"You are a helpful {self.config.knowledge_domain} expert.",
                                "Your responses MAY ONLY REFER TO THE FOLLOWING CONTEXT:",
                                "\n",
                                context,
                            ]
                        ),
                    ),
                    ChatBlock(
                        role="user",
                        content=query,
                    ),
                ]
            )
            # ensure that the response is relevant
            if not self.check_answer_is_relevant(query=query, answer=community_answer.content):
                logging.debug("community %s answer deemed irrelevant", community_name)
                continue

            if not self.check_statement_is_grounded(
                    statement=community_answer.content,
                    context=context,
            ):
                logging.debug("community %s answer deemed ungrounded", community_name)
                continue

            # otherwise, all good
            responses[community_name] = community_answer.content
            pass

        if not responses:
            return {}

        final_context = "\n".join(responses.values())
        final_answer = self.llm_client.chat_completion(
            [
                ChatBlock(
                    role="system",
                    content=" ".join(
                        [
                            f"You are a helpful {self.config.knowledge_domain} expert.",
                            "Your responses MAY ONLY REFER TO THE FOLLOWING CONTEXT:",
                            "\n",
                            final_context,
                        ]
                    ),
                ),
                ChatBlock(
                    role="user",
                    content=query,
                ),
            ]
        )
        responses["FINAL"] = final_answer.content
        return responses

    pass
