import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")


# Function to get environment variable with default and log if default is used
def get_env_with_default(key, default):
    value = os.getenv(key, default)
    if value == default:
        logger.info(f"{key}: {default} (default)")
    else:
        logger.info(f"{key}: {value} (environ)")

    if key == "CORS_ORIGIN":
        return value.split(",")
    return value


# Define default values
LLM_MODEL = get_env_with_default("LLM_MODEL", "sroecker/sauerkrautlm-7b-hero:latest")
LLM_HOST = get_env_with_default("LLM_HOST", "http://localhost:11434")
OLLAMA_EMBED_MODEL = get_env_with_default("OLLAMA_EMBED_MODEL", "nomic-embed-text")
QDRANT_CONNECTION_STRING = get_env_with_default(
    "QDRANT_CONNECTION_STRING", "http://localhost:6333"
)
VECTOR_STORE_COLLECTION = get_env_with_default("VECTOR_STORE_COLLECTION", "rag")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
LLMSHERPA_API_URL = get_env_with_default(
    "LLMSHERPA_API_URL", "http://localhost:5010/api/parseDocument?renderFormat=all"
)
DATA_FOLDER = get_env_with_default("DATA_FOLDER", "/data")
CORS_ORIGIN = get_env_with_default("CORS_ORIGIN", "http://localhost:3000")
