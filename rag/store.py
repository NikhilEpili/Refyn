"""Qdrant integration."""

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from app.config import settings
import structlog
from typing import Any

logger = structlog.get_logger()

client = AsyncQdrantClient(url=settings.qdrant_url)

async def init_collection(repo_id: str) -> None:
    """Initialize a Qdrant collection for a specific repository if it doesn't exist."""
    collection_name = f"refyn_{repo_id}"
    
    exists = await client.collection_exists(collection_name=collection_name)
    if not exists:
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1536, # text-embedding-3-small size
                distance=models.Distance.COSINE
            )
        )
        await logger.ainfo("Created Qdrant collection", collection=collection_name)

async def upsert_chunks(repo_id: str, points: list[models.PointStruct]) -> None:
    """Upsert vectors to Qdrant."""
    collection_name = f"refyn_{repo_id}"
    await init_collection(repo_id)
    await client.upsert(collection_name=collection_name, points=points)

async def search_context(repo_id: str, query_vector: list[float], limit: int = 12) -> list[dict[str, Any]]:
    """Search for relevant codebase chunks."""
    collection_name = f"refyn_{repo_id}"
    try:
        exists = await client.collection_exists(collection_name=collection_name)
        if not exists:
            return []
            
        results = await client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )
        return [hit.payload for hit in results if hit.payload is not None]
    except Exception as e:
        await logger.aerror("Qdrant search failed", error=str(e), collection=collection_name)
        return []
