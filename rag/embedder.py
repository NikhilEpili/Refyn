"""Embedding generation."""

from app.config import settings
from langchain_openai import OpenAIEmbeddings

def get_embedder() -> OpenAIEmbeddings:
    """Get the configured embedding model."""
    api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else ""
    return OpenAIEmbeddings(
        model="text-embedding-3-small", 
        api_key=api_key
    )

async def embed_query(text: str) -> list[float]:
    """Embed a single query string asynchronously."""
    embedder = get_embedder()
    return await embedder.aembed_query(text)

async def embed_chunks(texts: list[str]) -> list[list[float]]:
    """Embed a list of text chunks asynchronously."""
    if not texts:
        return []
    embedder = get_embedder()
    return await embedder.aembed_documents(texts)
