from dotenv import load_dotenv

load_dotenv()
import click

import logging
import os
import uvicorn
from ollama_rag_de.chat.router import chat_router
from ollama_rag_de.api.router import api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ollama_rag_de.settings import CORS_ORIGIN

app = FastAPI()

environment = os.getenv("ENVIRONMENT", "dev")  # Default to 'development' if not set

logger = logging.getLogger("uvicorn")
if environment == "dev":
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
if environment == "prod" or environment == "production":
    logger.warning(
        f"Running in production mode - CORS is active (allow: {CORS_ORIGIN})"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGIN,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(chat_router, prefix="/api/chat")
app.include_router(api_router, prefix="/api/v1")


@click.command()
@click.option(
    "-h",
    "--host",
    default="localhost",
    help="Host the server runs on. Default is `localhost`",
    type=click.STRING,
)
@click.option(
    "-c",
    "--collection",
    default="rag",
    help='Index collection name to use for the query. Default is "rag".',
    type=click.STRING,
)
@click.option(
    "-p",
    "--port",
    default=8000,
    help="Port to run the server on. (8000)",
    type=click.INT,
)
@click.option(
    "-d",
    "--debug",
    default=False,
    help="Run the server in debug mode.",
    type=click.BOOL,
    is_flag=True,
)
def chat_server(host: str, port: int, debug: bool, collection: str):
    """Start the chat server with uvicorn."""
    os.environ["COLLECTION"] = collection
    uvicorn.run(app="ollama_rag_de.server:app", host=host, reload=debug, port=port)


if __name__ == "__main__":
    """This block is executed when the script is run directly with default options"""
    uvicorn.run(app="ollama_rag_de.server:app", host="0.0.0.0", reload=True)


# old segement

# from uvicorn.reloaders.statreload import StatReload
# from uvicorn.main import run, get_logger
# reloader = StatReload(get_logger(run_config['log_level']))
# reloader.run(run, {
#     'app': app,
#     'host': run_config['api_host'],
#     'port': run_config['api_port'],
#     'log_level': run_config['log_level'],
#     'debug': 'true'
# })
