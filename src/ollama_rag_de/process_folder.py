import click
import json
from llmsherpa.readers import LayoutPDFReader, Document


def process_pdf(pdf_url: str, llmsherpa_api_url: str) -> Document:
    """Process a PDF file using llmsherpa and return a Document object.

    Args:
        pdf_url (str): The URL of the PDF file to process.
        llmsherpa_api_url (str): The URL of the llmsherpa API.
    """
    pdf_reader = LayoutPDFReader(llmsherpa_api_url)
    doc = pdf_reader.read_pdf(pdf_url)
    return doc


def output_document(
    doc: Document, output_abspath: str, format: str, include_section_info: bool = False
):
    """Write all sections of the document to a single file

    Args:
        doc (Document): The document to write.
        output_abspath (str): The output file path.
        format (str): The format to write the document in.
        include_section_info (bool): Include section information in the output.

    Returns:
        str: The output file path.
    """
    output_file_with_extension = (
        f"{output_abspath}.{format}"
        if format == "txt"
        else f"{output_abspath}.{format}.json"
    )

    match format:
        case "txt":
            output_string = doc.to_text()
        case "raw":
            output_string = json.dumps(doc.json)
        case "sections":
            output_string = json.dumps(
                [
                    section.to_context_text(include_section_info=include_section_info)
                    for section in doc.sections()
                ]
            )
        case "chunks":
            output_string = json.dumps(
                [
                    chunk.to_context_text(include_section_info=include_section_info)
                    for chunk in doc.chunks()
                ]
            )

    try:
        with open(output_file_with_extension, "w") as output_file:
            output_file.write(output_string)
    except Exception as e:
        click.echo(f"Error writing output file {output_file_with_extension}: {e}")
    finally:
        output_file.close()
    return output_file_with_extension
