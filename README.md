# MiniKG - A (mini) LLM-powered knowledge graph builder, retriever, and RAG system

*For instructive use, but also supporting easy hackability and quick POCs*

For a high-level look at GraphRAG and some of the design choices in `minikg`, check out the [companion article](https://blacktuskdata.com/graphrag_overview.html).


## Example

The example included in this repo is a knowledge graph built over transcripts of a few Meta earnings calls.

You can find the source PDFs of those calls [here](https://investor.fb.com/financials/default.aspx).
Note that they were converted to text with `pdftotext`, and commited to the repo [here](./examples/meta-call-transcripts/txts).

Here is a visualization of one 'community' from the resultant knowledge graph:
![AI products community](./examples/meta-call-transcripts/community-3.png "AI products")


### Build the example Meta earnings call GraphRAG system

```sh
export OPENAI_API_KEY=<>
export JINA_AI_API_KEY=<>
```

```sh
cd ./examples/meta-call-transcripts
./build.py
```

### Query over the resultant system

```sh
./query.py "What technological investments appear most likely to yield profit for Meta in 2025?"
```
