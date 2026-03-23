"""PostgreSQL write layer for feedback."""

import asyncpg
from app.config import settings
import structlog

logger = structlog.get_logger()

async def get_db_pool() -> asyncpg.Pool:
    """Get a connection pool for the database."""
    # In a full setup, this pool would be on app state. We create minimal connection for MVP.
    return await asyncpg.create_pool(settings.postgres_dsn)

async def insert_feedback(repo_id: str, comment_id: int, agent_type: str, reaction: int, confidence: float) -> None:
    """Insert a feedback reaction into the PostgreSQL database."""
    pool = await get_db_pool()
    query = """
    INSERT INTO feedback (repo_id, comment_id, agent_type, reaction, confidence)
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT DO NOTHING;
    """
    try:
        async with pool.acquire() as connection:
            await connection.execute(query, repo_id, comment_id, agent_type, reaction, confidence)
            await logger.adebug("Inserted feedback", comment_id=comment_id, reaction=reaction)
    except Exception as e:
        await logger.aerror("Failed to insert feedback", error=str(e))
    finally:
        await pool.close()
