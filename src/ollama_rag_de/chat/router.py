# from llama_index.core.callbacks import (
#     CallbackManager,
#     LlamaDebugHandler,
#     CBEventType,
# )

# llama_debug = LlamaDebugHandler(print_trace_on_end=True)
# callback_manager = CallbackManager([llama_debug])
import json
import logging
from typing import List
from fastapi.responses import StreamingResponse
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.query_engine import BaseQueryEngine

from ollama_rag_de.engine import get_chat_engine
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.core.chat_engine.types import ChatMessage
from llama_index.core.types import MessageRole
from pydantic import BaseModel

chat_router = r = APIRouter()

log = logging.getLogger("uvicorn")

class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]


@r.post("")
async def chat(
    request: Request,
    data: _ChatData,
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
):
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]

    # query chat engine
    #try:
        # astream did not work
    #response = await chat_engine.astream_chat(lastMessage.content)#, messages)
    chat_engine : BaseQueryEngine
    response = chat_engine.query(lastMessage.content)  
    # response = chat_engine.stream_chat(lastMessage.content, messages)
    #response = chat_engine.stream_chat(lastMessage.content, [])
    # except Exception as e:
    #     print(f"Could not stream chat {str(e)}")
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Could not stream chat {str(e)}",
    #     )

    # stream response
    # async def event_generator():
    #     async for token in response.async_response_gen():
    #         # If client closes connection, stop sending events
    #         if await request.is_disconnected():
    #             break
    #         yield token
    
    # event_pairs = llama_debug.get_llm_inputs_outputs()
    # print(event_pairs)
    # print(event_pairs[0][1].payload.keys())
    # print(event_pairs[0][1].payload["response"])
    
    async def event_generator():
        #async for token in response.async_response_gen(): #response_gen:
        for token in response.response_gen: #response_gen:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            
            yield token
        try:
            # metadata = "\n\n".join(set([f"{node.metadata['Dateiname']} ({node.metadata['Vollständiger Pfad']})" for node in response.source_nodes]))
            metadata = "\n\n".join(set([f"{node.metadata['Vollständiger Pfad']}" for node in response.source_nodes]))
            yield f"\n\n--\n\nQuellen:\n\n {metadata}"
        except:
            print("Could not get metadata")
    log.info(f"Query: {lastMessage.content}\n" + "\n".join([json.dumps(node.metadata, indent=4) for node in response.source_nodes]))
            
        #yield ".".join(response.)
    
    return StreamingResponse(event_generator(), media_type="text/plain")

