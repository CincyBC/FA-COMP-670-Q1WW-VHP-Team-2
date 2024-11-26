import os
import chainlit as cl
import openai

import torch

import os
from typing import List, Optional

from chainlit import AskUserMessage, Message, on_chat_start

from llama_index.core import KeywordTableIndex, SimpleDirectoryReader
from llama_index.core.llms import ChatMessage
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine

from huggingface_hub import login

HF_TOKEN: Optional[str] = os.getenv("HUGGING_FACE_TOKEN")

MODEL_NAME="mistralai/Mixtral-8x7B-Instruct-v0.1"
# MODEL_NAME = "HuggingFaceH4/zephyr-7b-alpha"
DATA_DIR = "data"

# Create the data directory if it does not exist
os.makedirs(DATA_DIR, exist_ok=True)

if HF_TOKEN:
    login(token=HF_TOKEN)
else:
    print("HUGGING_FACE_TOKEN not found.")
    
print("Loading data.")
documents = SimpleDirectoryReader("data").load_data()
print("Data loaded!")

# Load the tokenizer and model
# print("Loading tokenizer.")
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_TOKEN)

# print("Loading model.")
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_NAME, token=HF_TOKEN, device_map="auto"
# )
# llm = HuggingFaceInferenceAPI(
#     repo_id=MODEL_NAME,
#     token=HF_TOKEN,
#     max_new_tokens=256,
#     temperature=0.7,
#     top_k=50,
#     top_p=0.95,
# )
# index = VectorStoreIndex.from_documents(documents, llm=llm)
# query_engine = index.as_query_engine()
# print("Model loaded!")

@cl.on_chat_start
async def main():
    user_id = cl.user_session.get("id")
    greeting_msg = cl.Message(content="Hello! How can I assist you?")
    await greeting_msg.send()
    print(f"Session started for user: {user_id}")

# Handle user input
@cl.on_message
async def handle_message(message: cl.Message):
    user_id = cl.user_session.get("id")
    user_input = message.content.strip()
    res_content = simulate_response(user_input)
    res_msg = cl.Message(content=res_content)

    try:
        await res_msg.send()
    except Exception as e:
        error_content="I've encountered an error. Can you try again?"
        await cl.Message(content=error_content).send()
        print(f"{e}")

@cl.on_chat_end
def end():
    user_id = cl.user_session.get("id")
    print(f"Session ended for user: {user_id}")

# Placeholder for generating a response
def simulate_response(user_input: str) -> str:
    return f"(Simulated Response): You said: '{user_input}'."