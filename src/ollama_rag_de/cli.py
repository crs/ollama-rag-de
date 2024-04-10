import click
import pathlib
from .process_folder import ingestion_pipeline
from .vector_store import get_vector_store_index

from .settings import LLMSHERPA_API_URL, VECTOR_STORE_COLLECTION


@click.command()
@click.argument("folder_path", type=click.Path(exists=True))
@click.option(
    "-llm",
    "--llmsherpa_api_url",
    default=LLMSHERPA_API_URL,
    help=f'URL of the LLMSherpa API to use for processing the PDFs. Default is "{LLMSHERPA_API_URL}"',
    type=click.STRING,
)
@click.option(
    "-o",
    "--output",
    # default="output",
    help='Output folder for the processed data. Default is "output".',
    type=click.Path(exists=False),
)
@click.option(
    "-f",
    "--format",
    default="chunks",
    help='Output format for the processed data. Default is "chunks"',
    type=click.Choice(["txt", "raw", "sections", "chunks"]),
)
@click.option(
    "-r",
    "--recursive",
    default=False,
    is_flag=True,
    help="Process the folder recursively, otherwise only the top level is processed.",
)
@click.option(
    "-db",
    "--database",
    default=VECTOR_STORE_COLLECTION,
    help='Store the processed data to "qdrant". Default collection is "rag" ',
    type=click.STRING,
)
@click.option(
    "-si",
    "--include_section_info",
    help="Include section information in the output.",
    is_flag=True,
    default=False,
)
@click.option(
    "-cs",
    "--clear_store",
    help="Clear the vector store before outputting the data.",
    is_flag=True,
    default=False,
)
def entrypoint(
    folder_path: str,
    output: pathlib.Path,
    llmsherpa_api_url: str,
    format: str,
    recursive: bool,
    database: str,
    include_section_info: bool,
    clear_store: bool,
):
    """Process a folder of pdf input data for Ollama and store the documents (also in a database)."""
    loggerfunc = click.echo
    ingestion_pipeline(
        loggerfunc,
        folder_path,
        output,
        llmsherpa_api_url,
        format,
        recursive,
        database,
        include_section_info,
        clear_store,
    )


@click.command()
@click.argument("question", type=click.STRING)
@click.option(
    "-db",
    "--collection",
    default=VECTOR_STORE_COLLECTION,
    help='Index collection name to use for the query. Default is "rag".',
    type=click.STRING,
)
def answer_question(question: str, collection: str):
    """Answer a question using the index."""
    # click.echo(f"Using: {collection}")
    index = get_vector_store_index(collection=collection)
    query_engine = index.as_query_engine()

    response = query_engine.query(question)
    click.echo(response)
    metadata = [node.metadata["Dateiname"] for node in response.source_nodes]
    # click.echo(response.get_formatted_sources(length=1000))
    click.echo("\n---\nQuellen:\n" + "\n".join(metadata))
