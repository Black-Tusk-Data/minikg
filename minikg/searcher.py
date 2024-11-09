class KgSearcher:
    """
    Kind of just a stub to get ideas out.

    A top-level query looks like:
     - ask each communitiy the question
     - take the combined answers from each community,
       and perform a final super 'answer'

    Within a community, a query looks like:
     - cosine similarity on any relevant nodes or edges
     - can simply include all those in a RAG request,
       or could also take a whole meaningful subgraph
    """
    pass
