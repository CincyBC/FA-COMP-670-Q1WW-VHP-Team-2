from llama_index.core.retrievers import BaseRetriever
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.core import PromptTemplate
from llama_index.llms.groq import Groq



# This CustomQueryEngine class came from this example https://docs.llamaindex.ai/en/stable/examples/query_engine/custom_query_engine/
class RAGStringQueryEngine(CustomQueryEngine):
    """RAG String Query Engine."""
    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: Groq
    qa_prompt: PromptTemplate

    def custom_query(self, query_str: str):
        nodes = self.retriever.retrieve(query_str)

        context_str = "\n\n".join([n.node.get_content() for n in nodes])
        return self.response_synthesizer.synthesize(qa_prompt, context_str, query_str)
        # response = self.llm.complete(
        #     qa_prompt.format(context_str=context_str, query_str=query_str)
        # )

        # return str(response)