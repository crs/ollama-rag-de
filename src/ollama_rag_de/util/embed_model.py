import click
from pathlib import Path 
from sentence_transformers import SentenceTransformer

                            
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from transformers import AutoTokenizer, AutoModelForMaskedLM

default_model_name = "VAGOsolutions/SauerkrautLM-Gemma-7b" # or 'bert-base-uncased'
default_cache = Path.home() / '.cache/huggingface/hub'

@click.command()
@click.argument('model_name', default=default_model_name, type=click.STRING)
@click.option('-c', '--cache_dir', default=default_cache, help='The directory to store the model.', type=click.Path(exists=False))
@click.option('-a', '--api_key', default="None", help='The API key to use for downloading the model.', type=click.STRING)
def cache_embed_model(model_name, cache_dir, api_key=None):
    """Download and store the embedding model (default is:) locally."""
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir, token=api_key)
    get_tokenizer(model_name, cache_dir, api_key)
    get_model(model_name, cache_dir, api_key)
    model = AutoModelForMaskedLM.from_pretrained(model_name, cache_dir=cache_dir, token=api_key)
    return model

def get_tokenizer(model_name=default_model_name, cache_dir=default_cache, api_key=None):
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir, token=api_key)
    return tokenizer

def get_model(model_name=default_model_name, cache_dir=default_cache, api_key=None):
    model = AutoModelForMaskedLM.from_pretrained(model_name, cache_dir=cache_dir, token=api_key)
    return model
