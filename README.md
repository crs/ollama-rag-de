# Ollama RAG Generator (German edition)

A tool to digest PDF files for Large Language Models and serving them via a REST API, including their source references.

The command line toolkit that provides methods:
- `ppf`: to preprocess PDF files and create context augmented chunks that are stored into a Qdrant vector database collection.
- `ask`: to send a query to the LLM engine
- `chat_server`: to start a FastAPI chat server interface that uses the LLM engine to answer questions



## Prerequisites

1. Get your https://github.com/nlmatics/nlm-ingestor up and running:
```bash
docker run --rm -p 5010:5001 ghcr.io/nlmatics/nlm-ingestor:latest
```

2. You need to have a running instance of Qdrant. You can use the following command to start a Qdrant instance:
```bash
docker run --rm -p 6333:6333 -p 6334:6334 -v /tmp/qdrant:/data qdrant/qdrant:latest
```

3. You need to have a running instance of Ollama. You can use the following command to start a Ollama instance:
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```
See more at documentation at [Docker Hub](https://hub.docker.com/r/ollama/ollama)

## Run the preprocessor

Clone the repository and install the dependencies:

```bash
poetry install
```
and then run the preprocessor:

```bash
ppf --help
```

Output:
```
Usage: ppf [OPTIONS] FOLDER_PATH

  Process a folder of OLLAMA pdf input data.

Options:
  -llm, --llmsherpa_api_url TEXT  URL of the LLMSherpa API to use for
                                  processing the PDFs. Default is "http://loca
                                  lhost:5010/api/parseDocument?renderFormat=al
                                  l"
  -o, --output PATH               Output folder for the processed data.
                                  Default is "output".
  -f, --format [txt|raw|sections|chunks]
                                  Output format for the processed data.
                                  Default is "chunks"
  -r, --recursive                 Process the folder recursively, otherwise
                                  only the top level is processed.
  -db, --database TEXT            Store the processed data to "qdrant".
                                  Default collection is "rag"
  -si, --include_section_info     Include section information in the output.
  --help                          Show this message and exit.
```

In order to preprocess a folder of PDF input data, run the following command:

```bash
ppf '/mnt/OneDrive/Shared Files' -db rag -o '/tmp' -r
```
This reads the PDF files located in specified folder recursively and stores the processed data in the `/tmp` folder. Also, the processed data is stored in the `rag` collection in the `qdrant` database.

## Ask questions

## Run the chat server

To start the chat server, run the following command:

```bash
chat_server --help

Usage: chat_server [OPTIONS]

  Start the chat server with uvicorn.

Options:
  -h, --host TEXT        Host the server runs on. Default is `localhost`
  -c, --collection TEXT  Index collection name to use for the query.
                         Default is "rag".
  -p, --port INTEGER     Port to run the server on. (8000)
  -d, --debug            Run the server in debug mode.
  --help                 Show this message and exit.
  ```