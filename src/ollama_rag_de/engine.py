import os, logging
from .settings import VECTOR_STORE_COLLECTION

# from .vector_store import get_vector_store_index as get_index
from .vector_store import get_vector_store_index  # , get_llm

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts import ChatPromptTemplate

# from llama_index.core.memory import ChatMemoryBuffer
# Text QA Prompt
logger = logging.getLogger("uvicorn")

chat_text_qa_msgs = [
    ChatMessage(
        role=MessageRole.SYSTEM,
        content=(
            "Antworte immer auf die Frage, die dir gestellt wird. Die Antwort soll immer auf Deutsch sein. "
        ),
    ),
    ChatMessage(
        role=MessageRole.USER,
        content=(
            "Der Kontext lautet:\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Basierend auf dem Kontext und ohne voriges Wissen,"
            "antworte (immer in deutscher Sprache!) auf diese Frage: {query_str}\n"
        ),
    ),
]
text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)

chat_refine_msgs = [
    ChatMessage(
        role=MessageRole.SYSTEM,
        content=(
            "Antworte immer auf die Frage, die dir gestellt wird. Die Antwort soll immer auf Deutsch sein. Erfinde keinen Inhalt"
        ),
    ),
    ChatMessage(
        role=MessageRole.USER,
        content=(
            "Wir haben den Kontext aktualisiert. Bitte verfeinere deine "
            "Antwort mit folgendem Kontext:\n"
            "------------\n"
            "{context_msg}\n"
            "------------\n"
            "Basierend auf dem Kontext und ohne voriges Wissen,"
            "verfeinere deine Antwort auf die Frage (und antworte auf Deutsch!): {query_str}. "
            "Wenn der Kontext keine Hilfe ist, gib die ursprüngliche Antwort aus.\n"
            "Ursprüngliche Antwort: {existing_answer}"
        ),
    ),
]
refine_template = ChatPromptTemplate(chat_refine_msgs)


def get_chat_engine():
    # engine = get_index().as_chat_engine()
    logger.debug(f"Running with {VECTOR_STORE_COLLECTION}")
    # engine = get_vector_store_index(collection=os.environ['COLLECTION']).as_chat_engine(
    #      similarity_top_k=3,
    #      chat_mode="context", # "condense_plus_context",
    #      llm=get_llm(),
    #      memory=ChatMemoryBuffer.from_defaults(token_limit=1500),
    #      text_qa_template=text_qa_template,
    #      refine_template=refine_template
    # )

    engine = get_vector_store_index(collection=VECTOR_STORE_COLLECTION).as_query_engine(
        streaming=True,
        similarity_top_k=3,
    )

    return engine
