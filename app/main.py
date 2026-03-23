"""FastAPI entrypoint for Refyn AI."""

from fastapi import FastAPI, Request, BackgroundTasks, Header
import structlog
from contextlib import asynccontextmanager
from app.webhook_handler import verify_signature, process_pull_request_event
from feedback.listener import handle_reaction_event
from feedback.scheduler import start_scheduler
from dashboard.router import router as dashboard_router
import json

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for FastAPI application."""
    await logger.ainfo("Starting Refyn AI", version="0.1.0")
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()
    await logger.ainfo("Shutting down Refyn AI")

app = FastAPI(
    title="Refyn AI",
    description="The code reviewer that learns your team",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(dashboard_router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
    
@app.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str | None = Header(default=None)
) -> dict[str, str]:
    """Receive and process GitHub App webhooks."""
    body = await verify_signature(request)
    payload = json.loads(body.decode("utf-8"))
    
    if x_github_event == "pull_request":
        background_tasks.add_task(process_pull_request_event, payload)
    elif x_github_event == "pull_request_review_comment":
        background_tasks.add_task(handle_reaction_event, payload)
        
    return {"status": "received"}
