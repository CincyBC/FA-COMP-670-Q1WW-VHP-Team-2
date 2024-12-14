import os
import chainlit as cl
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.groq import Groq
from llama_index.core import Settings, VectorStoreIndex, get_response_synthesizer
import qdrant_client
import logging
from llama_index.vector_stores.qdrant import QdrantVectorStore
from context.rag_string_query_engine import RAGStringQueryEngine, qa_prompt
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
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="mixedbread-ai/mxbai-embed-large-v1"
    )
    Settings.streaming = True
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    Settings.num_output = 512
    Settings.context_window = 3900

    # This section of code creates the index and retriever
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, settings=Settings)
    retriever = index.as_retriever()
    synthesizer = get_response_synthesizer(response_mode="compact")

    query_engine = RAGStringQueryEngine(
        retriever=retriever,
        response_synthesizer=synthesizer,
        qa_prompt=qa_prompt,
        llm=llm,
    )

    #This final section gets the conversation started
    cl.user_session.set("conversation_history", [
        {"role": "system", "content": opening_context}
    ])
    cl.user_session.set("query_engine", query_engine)

    # await cl.Message(
    #     author="assistant", content="Hello! I am a Franklin University automated advisor created by Team 2 in Comp-670. How may I assist you?"
    # ).send()

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Admissions Guidance",
            message="Can you help me with the admissions process for Franklin University? Start by asking me if I'm a first-time student, a transfer student, or an international student.",
            icon="/public/icons/school.svg",
            ),

        cl.Starter(
            label="Tuition & Financial Aid",
            message="Can you provide details about tuition costs and financial aid? Start by asking if I need information about scholarships, military student aid, or other financial resources.",
            icon="/public/icons/paid.svg",
            ),
        cl.Starter(
            label="University Resources",
            message="Can you guide me to available student resources, like the library, tutoring services, or mental health support? Start by asking me what kind of help I need.",
            icon="/public/icons/books.svg",
            ),
        cl.Starter(
            label="University Leadership",
            message="Can you provide information about the university's leadership? Start by asking if I need to know the University President's name or where to find the names of the University Board members or other faculty.",
            icon="/public/icons/groups.svg",
            ),
        ]

@cl.on_message
async def main(message: cl.Message):

    # This section of code logs the conversation history, which is not really utilized
    conversation_history = cl.user_session.get("conversation_history")
    logging.info(f"User Message: {message.content}")
    conversation_history.append({"role": "user", "content": message.content})

    # This section of code gets the query engine and sends the response
    query_engine = cl.user_session.get("query_engine") # type: RetrieverQueryEngine

    res = await cl.make_async(query_engine.query)(message.content)
    msg = cl.Message(content="", author="assistant")
    for token in res.response.split():
        await msg.stream_token(token + " ")

    await msg.send()
    logging.info(f"Assistant Response: {res.response}")

    # This section of code logs the conversation history
    conversation_history.append({"role": "assistant", "content": res.response})
    cl.user_session.set("conversation_history", conversation_history)

