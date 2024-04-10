import click, pathlib, json
from os import path
from llmsherpa.readers import LayoutPDFReader, Document
from .vector_store import clear_vector_store, output_to_store
from .util.file import sizeof_fmt


def ingestion_pipeline(
    loggerfunc: callable,
    folder_path: str,
    output: pathlib.Path,
    llmsherpa_api_url: str,
    format: str,
    recursive: bool,
    database: str,
    include_section_info: bool,
    clear_store: bool,
):
    working_directory = pathlib.Path(folder_path)
    file_iterator = (
        working_directory.rglob("*.pdf")
        if recursive
        else working_directory.glob("*.pdf")
    )
    loggerfunc(f'Using "{format}" conversion on input directory: {folder_path}...')

    working_directory = path.abspath(working_directory)

    if not output:
        output = pathlib.Path("/tmp")

    if output:
        output_path = pathlib.Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        loggerfunc(f"Output {format} to directory: {output_path}")

    good_files = 0
    skipped_files = 0
    if database and clear_store:
        clear_vector_store(collection=database)

    for i, file in enumerate(file_iterator):
        try:
            absolute_path = path.abspath(file)
            file_name = path.basename(file)

            document = process_pdf(str(absolute_path), llmsherpa_api_url)
            if output:
                output_abspath = path.join(output, path.splitext(file_name)[0])
                output_filename = output_document(
                    document, output_abspath=output_abspath, format_type=format
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
            loggerfunc(
                f"{i+1 : >3} {origin_file_size : >8} -> {processed_file_size : >8}: {file_name}"
            )
            good_files += 1
        except Exception as e:
            loggerfunc(f"Error processing PDF {absolute_path}: {e}")
            skipped_files += 1
    loggerfunc(
        f"Digested {good_files}/{good_files+skipped_files} files ({skipped_files} skipped)"
    )
    return {
        "good_files": good_files,
        "skipped_files": skipped_files,
        "total_files": good_files + skipped_files,
    }


def process_pdf(pdf_url: str, llmsherpa_api_url: str) -> Document:
    """Process a PDF file using llmsherpa and return a Document object.

    Args:
        pdf_url (str): The URL of the PDF file to process.
        llmsherpa_api_url (str): The URL of the llmsherpa API.
    """
    pdf_reader = LayoutPDFReader(llmsherpa_api_url)
    doc = pdf_reader.read_pdf(pdf_url)
    return doc


def output_document(doc, output_abspath, format_type, include_section_info=False):
    """Write all sections of the document to a single file

    Args:
        doc (Document): The document to write.
        output_abspath (str): The output file path.
        format_type (str): The format to write the document in.
        include_section_info (bool): Include section information in the output.

    Returns:
        str: The output file path.
    """
    output_file_with_extension = (
        f"{output_abspath}.{format_type}"
        if format_type == "txt"
        else f"{output_abspath}.{format_type}.json"
    )

    if format_type == "txt":
        output_string = doc.to_text()
    elif format_type == "raw":
        output_string = json.dumps(doc.json)
    elif format_type == "sections":
        output_string = json.dumps(
            [
                section.to_context_text(include_section_info=include_section_info)
                for section in doc.sections()
            ]
        )
    elif format_type == "chunks":
        output_string = json.dumps(
            [
                chunk.to_context_text(include_section_info=include_section_info)
                for chunk in doc.chunks()
            ]
        )
    else:
        raise ValueError(f"Unsupported format: {format_type}")

    try:
        with open(output_file_with_extension, "w") as output_file:
            output_file.write(output_string)
    except Exception as e:
        click.echo(f"Error writing output file {output_file_with_extension}: {e}")
    finally:
        output_file.close()
    return output_file_with_extension


# def output_document(
#     doc: Document, output_abspath: str, format: str, include_section_info: bool = False
# ):
#     """Write all sections of the document to a single file

#     Args:
#         doc (Document): The document to write.
#         output_abspath (str): The output file path.
#         format (str): The format to write the document in.
#         include_section_info (bool): Include section information in the output.

#     Returns:
#         str: The output file path.
#     """
#     output_file_with_extension = (
#         f"{output_abspath}.{format}"
#         if format == "txt"
#         else f"{output_abspath}.{format}.json"
#     )

#     match format:
#         case "txt":
#             output_string = doc.to_text()
#         case "raw":
#             output_string = json.dumps(doc.json)
#         case "sections":
#             output_string = json.dumps(
#                 [
#                     section.to_context_text(include_section_info=include_section_info)
#                     for section in doc.sections()
#                 ]
#             )
#         case "chunks":
#             output_string = json.dumps(
#                 [
#                     chunk.to_context_text(include_section_info=include_section_info)
#                     for chunk in doc.chunks()
#                 ]
#             )

#     try:
#         with open(output_file_with_extension, "w") as output_file:
#             output_file.write(output_string)
#     except Exception as e:
#         click.echo(f"Error writing output file {output_file_with_extension}: {e}")
#     finally:
#         output_file.close()
#     return output_file_with_extension
