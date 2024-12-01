import os
import chainlit as cl
from groq import AsyncGroq
from context.opening_context import opening_context

client = AsyncGroq(api_key=os.environ.get("GROQ_TOKEN"))

@cl.on_chat_start
async def start():
    cl.user_session.set("model", "llama3-8b-8192")
    cl.user_session.set("streaming", True)
    cl.user_session.set("temperature", 0.5)
    cl.user_session.set("max_tokens", 1024)

    cl.user_session.set("conversation_history", [
        {"role": "system", "content": opening_context}
    ])
    await cl.Message(
        author="Assistant", content="Hello! I am a Franklin University automated advisor. How may I assist you?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    model = cl.user_session.get("model")
    streaming = cl.user_session.get("streaming")
    temperature = cl.user_session.get("temperature")
    max_tokens = cl.user_session.get("max_tokens")

    conversation_history = cl.user_session.get("conversation_history")

    conversation_history.append({"role": "user", "content": message.content})

    stream = await client.chat.completions.create(
        messages=conversation_history,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=streaming,
    )

    msg = cl.Message(content="")

    full_response = ""
    if streaming:
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                await msg.stream_token(content)
        await msg.send()
    else:
        response = await stream
        full_response = response.choices[0].message.content
        await cl.Message(content=full_response).send()

    conversation_history.append({"role": "assistant", "content": full_response})

    cl.user_session.set("conversation_history", conversation_history)