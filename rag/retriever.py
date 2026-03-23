"""Context retrieval for the review pipeline."""

from rag.embedder import embed_query
from rag.store import search_context
import structlog

logger = structlog.get_logger()

async def retrieve_context(repo_id: str, pr_diff: str) -> list[str]:
    """
    Given a PR unified diff, retrieve the most relevant codebase chunks.
    We embed the first 512 tokens of the diff to use as the query vector.
    """
    if not pr_diff or not pr_diff.strip():
        return []
        
    # Simplify diff and embed first ~2000 chars to avoid token limit errors
    query_text = pr_diff[:2000]
    
    try:
        query_vector = await embed_query(query_text)
        results = await search_context(repo_id, query_vector, limit=12)
        
        # Format the retrieved context for the LLM
        context_chunks = []
        for res in results:
            file_path = res.get("file_path", "unknown")
            content = res.get("content", "")
            chunk_type = res.get("chunk_type", "unknown")
            context_chunks.append(f"--- File: {file_path} ({chunk_type}) ---\n{content}\n")
            
        return context_chunks
    except Exception as e:
        await logger.aerror("Context retrieval failed", error=str(e), repo_id=repo_id)
        return []
