import os
import chainlit as cl
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.groq import Groq
from llama_index.core import Settings, VectorStoreIndex, StorageContext, ChatPromptTemplate, PromptTemplate, get_response_synthesizer
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.response_synthesizers import BaseSynthesizer
import qdrant_client
import logging
from llama_index.vector_stores.qdrant import QdrantVectorStore
from context.rag_string_query_engine import RAGStringQueryEngine, qa_prompt
from context.opening_context import opening_context

@cl.on_chat_start
async def start():
    vector_store = QdrantVectorStore(
    collection_name="vh_collection", 
    client=qdrant_client.QdrantClient(url=os.environ['CN_QDRANT_URL'], api_key=os.environ['CN_QDRANT_TOKEN'])
    )

    llm = Groq(model="llama3-8b-8192", 
    api_key=os.environ['GROQ_TOKEN'], 
    temperature=0.1, 
    api_url='https://api.groq.com/openai/v1')
    
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="all-MiniLM-L6-v2"
    )
    Settings.streaming = True
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    Settings.num_output = 512
    Settings.context_window = 3900
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, settings=Settings)
    retriever = index.as_retriever()
    synthesizer = get_response_synthesizer(response_mode="compact")

    query_engine = RAGStringQueryEngine(
        retriever=retriever,
        response_synthesizer=synthesizer,
        qa_prompt=qa_prompt,
        llm=llm,
    )
    cl.user_session.set("conversation_history", [
        {"role": "system", "content": opening_context}
    ])
    cl.user_session.set("query_engine", query_engine)

    await cl.Message(
        author="assistant", content="Hello! I am a Franklin University automated advisor. How may I assist you?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    conversation_history = cl.user_session.get("conversation_history")
    streaming = cl.user_session.get("streaming")
    conversation_history.append({"role": "user", "content": message.content})

    query_engine = cl.user_session.get("query_engine") # type: RetrieverQueryEngine

    res = await cl.make_async(query_engine.query)(message.content)
    msg = cl.Message(content="", author="assistant")
    for token in res.response.split():
        await msg.stream_token(token + " ")

    await msg.send()

    conversation_history.append({"role": "assistant", "content": full_response})

    cl.user_session.set("conversation_history", conversation_history)

