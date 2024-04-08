import click
import pathlib
from os import path
from .util.file import sizeof_fmt
from .process_folder import process_pdf, output_document
from .vector_store import output_to_store, get_vector_store_index

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
    default="output",
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
    default="rag",
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
def entrypoint(
    folder_path: str,
    output: pathlib.Path,
    llmsherpa_api_url: str,
    format: str,
    recursive: bool,
    database: bool,
    include_section_info: bool,
):
    """Process a folder of pdf input data for Ollama and store the documents (also in a database)."""

    working_directory = pathlib.Path(folder_path)

    output_path = pathlib.Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    file_iterator = (
        working_directory.rglob("*.pdf")
        if recursive
        else working_directory.glob("*.pdf")
    )
    click.echo(f'Using "{format}" conversion on input directory: {folder_path}...')

    working_directory = path.abspath(working_directory)

    for i, file in enumerate(file_iterator):
        try:
            absolute_path = path.abspath(file)
            file_name = path.basename(file)
            output_abspath = path.join(output, path.splitext(file_name)[0])
            document = process_pdf(str(absolute_path), llmsherpa_api_url)
            output_filename = output_document(
                document, output_abspath=output_abspath, format=format
            )

            file_path_rel_to_input_dir = path.relpath(absolute_path, working_directory)
            if database:
                output_to_store(
                    doc=document,
                    full_path=str(file_path_rel_to_input_dir),
                    collection=database,
                    include_section_info=include_section_info,
                )

            origin_file_size = sizeof_fmt(file.stat().st_size)
            processed_file_size = sizeof_fmt(path.getsize(output_filename))
            click.echo(
                f"{i+1 : >3} {origin_file_size : >8} -> {processed_file_size : >8}: {file_name}:  ({format})..."
            )
        except Exception as e:
            click.echo(f"Error processing PDF {absolute_path}: {e}")


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
