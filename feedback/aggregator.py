"""Calculate strictness weights and sync to Redis."""

from feedback.store import get_db_pool
import redis.asyncio as redis
from app.config import settings
import structlog

logger = structlog.get_logger()

async def compute_strictness_weights() -> None:
    """
    Compute acceptance rates per agent per repo and write strictness weights to Redis.
    Uses rolling window logic: >= 70% positive = +1 strictness, <= 40% = -1 strictness.
    """
    pool = await get_db_pool()
    redis_client = redis.Redis.from_url(settings.redis_url)
    
    query = """
    SELECT repo_id, agent_type, 
           COUNT(*) as total_reactions,
           SUM(CASE WHEN reaction > 0 THEN 1 ELSE 0 END) as positive_reactions
    FROM feedback
    WHERE created_at > NOW() - INTERVAL '30 days'
    GROUP BY repo_id, agent_type
    """
    
    try:
        async with pool.acquire() as connection:
            records = await connection.fetch(query)
            
        for record in records:
            repo_id = record["repo_id"]
            agent_type = record["agent_type"]
            total = record["total_reactions"]
            pos = record["positive_reactions"]
            
            if total >= 5: # Minimum threshold to adjust
                acceptance_rate = pos / total
                strictness_change = 0.0
                if acceptance_rate >= 0.70:
                    strictness_change = 1.0
                elif acceptance_rate <= 0.40:
                    strictness_change = -1.0
                    
                new_strictness = max(1.0, min(5.0, 3.0 + strictness_change))
                
                key = f"strictness:{repo_id}:{agent_type}"
                await redis_client.set(key, str(new_strictness), ex=90000) # 25h TTL
                await logger.ainfo("Updated strictness", repo=repo_id, agent=agent_type, new_strictness=new_strictness)
                
    except Exception as e:
        await logger.aerror("Failed to compute strictness weights", error=str(e))
    finally:
        await pool.close()
        await redis_client.aclose()
