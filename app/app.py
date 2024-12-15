import os
import chainlit as cl
from llama_index.embeddings.huggingface import HuggingFaceInferenceAPIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.groq import Groq
from llama_index.core import Settings, VectorStoreIndex, get_response_synthesizer
from llama_index.core.base.llms.types import ChatMessage
import qdrant_client
import logging
from llama_index.vector_stores.qdrant import QdrantVectorStore
from context.qa_prompt import qa_prompt
from context.rag_string_query_engine import RAGStringQueryEngine
from context.opening_context import opening_context

@cl.on_chat_start
async def start():
    logging.info("Starting chat")

    # This section of code instantiates the vector store
    vector_store = QdrantVectorStore(
    collection_name="final_collection", 
    client=qdrant_client.QdrantClient(url=os.environ['QDRANT_URL'], api_key=os.environ['QDRANT_TOKEN'])
    )
    logging.info("Vector store created")

    # This section of code defines the llm
    llm = Groq(model="llama3-8b-8192", 
    api_key=os.environ['GROQ_TOKEN'], 
    temperature=0.1, 
    api_url='https://api.groq.com/openai/v1')
    
    Settings.llm = llm

    # This section of code sets up the embedding model
    Settings.embed_model = HuggingFaceInferenceAPIEmbedding(
        model_name="mixedbread-ai/mxbai-embed-large-v1",
        token=os.environ['HF_TOKEN'],
    )
    Settings.streaming = True
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    Settings.num_output = 512
    Settings.context_window = 3900

    # This section of code creates the index and retriever
    chat_engine = VectorStoreIndex.from_vector_store(vector_store=vector_store, settings=Settings).as_chat_engine(chat_mode="context", llm=llm, verbose=True)

    #This final section gets the conversation started
    cl.user_session.set("conversation_history", [ChatMessage(role="system", content=opening_context)])
    cl.user_session.set("query_engine", chat_engine)


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Admissions Guidance",
            message="Can you help me with the admissions process for Franklin University?",
            icon="/public/icons/school.svg",
            ),

        cl.Starter(
            label="Tuition & Financial Aid",
            message="Can you provide details about tuition costs and financial aid?",
            icon="/public/icons/paid.svg",
            ),
        cl.Starter(
            label="University Resources",
            message="Can you guide me to available student resources, like the library, tutoring services, or mental health support?",
            icon="/public/icons/books.svg",
            ),
        cl.Starter(
            label="University Leadership",
            message="Can you provide information about the university's leadership? Who is the University President?",
            icon="/public/icons/groups.svg",
            ),
        ]

@cl.on_message
async def main(message: cl.Message):

    # This section of code logs the conversation history, which is not really utilized
    conversation_history = cl.user_session.get("conversation_history")
    logging.info(f"User Message: {message.content}")
    message = ChatMessage(role="user", content=message.content)
    
    # This section of code gets the query engine and sends the response
    query_engine = cl.user_session.get("query_engine") 
    
    res = query_engine.chat(chat_history=conversation_history, message=message.content)                   
    
    conversation_history.append(message)
    msg = cl.Message(content="", author="assistant")
    logging.info(res)
    for token in res.response.split():
        await msg.stream_token(token + " ")

    await msg.send()
    logging.info(f"Assistant Response: {res.response}")

    # This section of code logs the conversation history
    conversation_history.append(ChatMessage(role="assistant", content=res.response))
    cl.user_session.set("conversation_history", conversation_history)

