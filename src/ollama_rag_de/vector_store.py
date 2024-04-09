# import click
# import functools
from os import path

# from pathlib import Path
from qdrant_client import QdrantClient
from llama_index.core import ServiceContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import StorageContext

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document as LlamaDoc

# from llama_index.core.embeddings.utils import resolve_embed_model


from llmsherpa.readers import Document as SherpaDoc
from llmsherpa.readers import Block as SherpaBlock

# from .util.embed_model import get_tokenizer, get_model

from .settings import (
    LLM_MODEL,
    LLM_HOST,
    OLLAMA_EMBED_MODEL,
    QDRANT_CONNECTION_STRING,
    VECTOR_STORE_COLLECTION,
    QDRANT_API_KEY,
)

# DEFAULT_LLM_MODEL = "sroecker/sauerkrautlm-7b-hero:latest"
# DEFAULT_LLM_HOST = "http://localhost:11434"
# DEFAULT_OLLAMA_EMBED_MODEL = "nomic-embed-text"
# QDRANT_CONNECTION_STRING = "http://localhost:6333"
# DEFAULT_VECTOR_STORE_COLLECTION = "rag"
# QDRANT_API_KEY = None


def get_qdrant_client(
    connection_string=QDRANT_CONNECTION_STRING, api_key=QDRANT_API_KEY
):
    """Get a Qdrant client.

    Args:
        connection_string (str): The connection string to use.
            Default is "http://localhost:6333".
        api_key (str): The API key to use. Default is None.

    Both the connection string and the API key can be set using environment variables:
    - `QDRANT_CONNECTION_STRING`
    - `QDRANT_API_KEY`
    """
    return (
        QdrantClient(connection_string)
        if api_key is None
        else QdrantClient(connection_string, api_key=api_key)
    )


def get_llm(llm_host=LLM_HOST, model=LLM_MODEL):
    """Get an Ollama instance.

    Args:
        llm_host (str): The host to use for the Ollama instance.
            Default is "http://localhost:11434".
        model (str): The model to use for the Ollama instance.
            Default is "sroecker/sauerkrautlm-7b-hero:latest".

    Returns:
        Ollama: The Ollama instance.

    The parameters can be set using environment variables:
    - `LLM_HOST`
    - `LLM_MODEL`
    """
    llm = Ollama(
        base_url=llm_host,
        model=model,
        request_timeout=160.0,
        temperature=0.0,
    )
    return llm


def get_ollama_embedding(model_name=OLLAMA_EMBED_MODEL, base_url=LLM_HOST):
    return OllamaEmbedding(model_name=model_name, base_url=base_url)


def get_context(model_name):
    """
    Get a service context with the given model name.

    Args:
        model_name (str): The model name to use.
    """
    # embed_model=get_embed_model(model_name=model_name) # BAAI/bge-small-en-v1.5')
    embed_model = get_ollama_embedding(model_name=model_name)
    llm = get_llm()
    service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
    return service_context


def get_index_store(client=None, collection="python") -> QdrantVectorStore:
    client = get_qdrant_client()
    return QdrantVectorStore(client=client, collection_name=collection)


def get_vector_store_index(
    collection=VECTOR_STORE_COLLECTION,
) -> VectorStoreIndex:
    """Get a vector store index.

    Args:
        collection (str): The collection to use for the index.
            Default is "rag".
    """
    client = get_qdrant_client()
    vector_store = QdrantVectorStore(client=client, collection_name=collection)

    # Possible Context Embed models
    # sroecker/sauerkrautlm-7b-hero - This was too slow
    # sentence-transformers/all-MiniLM-L6-v2
    # HuggingFace - intfloat/multilingual-e5-large")
    service_context = get_context(OLLAMA_EMBED_MODEL)

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        index_store=get_index_store(),
    )
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        service_context=service_context,
        storage_context=storage_context,
    )  #  embed_model="local:BAAI/bge-small-de-v1.5")
    if index is None:
        raise ValueError("Index is None")
    return index


def output_to_store(
    doc: SherpaDoc, full_path, collection="python", include_section_info=False
) -> None:
    """Output a document to the vector store.

    Args:
        doc (SherpaDoc): The document to output.
        full_path (str): The full path of the document.
        collection (str): The collection to output to.
        include_section_info (bool): Include section information in the output.
    """
    index = get_vector_store_index(collection=collection)
    chunk: SherpaBlock

    filename = path.basename(full_path)
    [title, extension] = path.splitext(filename)
    extra_info = {
        "Dateiname": filename,
        "Vollständiger Pfad": full_path,
        "Titel": title,
        "Dateiendung": extension,
    }
    for i, chunk in enumerate(doc.chunks()):
        index.insert(
            LlamaDoc(
                text=chunk.to_context_text(include_section_info=include_section_info),
                extra_info={
                    **extra_info,
                    "Kontext-Typ": "chunk",
                },
            ),
            ids=[f"{filename}-{i}"],
        )

    index.insert(
        LlamaDoc(
            text=doc.to_text(),
            extra_info={
                **extra_info,
                "Kontext-Typ": "document",
            },
        ),
        ids=[f"{filename}-document"],
    )
