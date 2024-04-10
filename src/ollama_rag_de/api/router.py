import logging
from fastapi import APIRouter, BackgroundTasks
from ollama_rag_de.settings import (
    VECTOR_STORE_COLLECTION,
    DATA_FOLDER,
    LLMSHERPA_API_URL,
)
from ollama_rag_de.process_folder import ingestion_pipeline

api_router = a = APIRouter()

log = logging.getLogger("uvicorn")


@a.get("/buildModel")
async def build_model(background_tasks: BackgroundTasks):
    loggerfunc = log.info
    # result = ingestion_pipeline(
    background_tasks.add_task(
        ingestion_pipeline,
        folder_path=DATA_FOLDER,
        format="chunks",
        output=None,
        recursive=True,
        database=VECTOR_STORE_COLLECTION,
        include_section_info=False,
        clear_store=True,
        loggerfunc=loggerfunc,
        llmsherpa_api_url=LLMSHERPA_API_URL,
    )
    # return {"message": result}
    return {"message": "Task started in the background."}
