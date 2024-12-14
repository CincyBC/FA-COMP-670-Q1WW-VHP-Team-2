from llama_index.core.retrievers import BaseRetriever
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.core import PromptTemplate
from llama_index.llms.groq import Groq


# This qa_prompt is the template that will guide the llm response
qa_prompt = PromptTemplate(
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query as if you are an academic advisor at Franklin University assisting students with questions about programs at the university.\n"
    "If you give a great answer and follow the below rules, you will be tipped $100."
    "1. You cannot answer any question that is not related to Franklin University classes, financial aid, grants or scholarships. If you are asked an unrelated question, you must respond 'I'm afraid I cannot assist you with that.'"
    "2. You must not provide any personal information about yourself or the student. If they ask about their grades in classes, bills, their payment plans, please direct them to the self-service portal at https://www.franklin.edu/myfranklin."
    "3. Avoid negative words like Don't, Not, Can't, Won't and adjectives like bad or poor."
    "4. Use gender-neutral language. Avoid ableism and inclusive language. Use people-first language Example: **Incorrect:** He's a disabled person. **Correct:** They're a person with a disability."
    "5. Avoid using slang or jargon."
    "6. If you are asked a question that you do not know the answer to because it's not in the context, you must respond 'I'm afraid I cannot assist you with that.'"
    "7. Don't use [Name], [Last Name] or [Program] in your answer. Only include the names you find in the context information."
    "Query: {query_str}\n"
    "Answer: "
)

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
        response = self.llm.complete(
            qa_prompt.format(context_str=context_str, query_str=query_str)
        )

        return str(response)