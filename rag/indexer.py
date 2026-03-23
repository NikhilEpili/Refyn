"""Codebase indexing pipeline."""

from rag.chunker import chunk_file
from rag.embedder import embed_chunks
from rag.store import upsert_chunks
from qdrant_client.http import models
import uuid
import datetime

async def index_repository(repo_id: str, files_dict: dict[str, str]) -> None:
    """
    Index a dictionary of file paths to their string content.
    This simulates cloning a repo and indexing its files.
    """
    points = []
    
    for file_path, content in files_dict.items():
        if not file_path.endswith(".py"): # MVP: python only
            continue
            
        file_chunks = chunk_file(file_path, content, language="python")
        
        # Batch embed
        if file_chunks:
            texts_to_embed = [chunk["content"] for chunk in file_chunks]
            embeddings = await embed_chunks(texts_to_embed)
            
            for i, chunk in enumerate(file_chunks):
                payload = {
                    "repo_id": repo_id,
                    "file_path": file_path,
                    "chunk_type": chunk["chunk_type"],
                    "language": "python",
                    "content": chunk["content"],
                    "last_modified": datetime.datetime.now(datetime.UTC).isoformat()
                }
                points.append(
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embeddings[i],
                        payload=payload
                    )
                )
                
    if points:
        await upsert_chunks(repo_id, points)
