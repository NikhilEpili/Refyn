"""FastAPI router for the metric dashboard."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/{repo_id}", response_class=HTMLResponse)
async def get_dashboard(request: Request, repo_id: str):
    """Serve the dashboard HTML for a given repository."""
    # For MVP we return a hardcoded demo HTML page to showcase the UI.
    html_content = f"""
    <html>
        <head>
            <title>Refyn AI Dashboard - {repo_id}</title>
            <style>
                body {{ font-family: sans-serif; padding: 2rem; background: #0f172a; color: #f8fafc; }}
                h1 {{ color: #38bdf8; }}
                .card {{ background: #1e293b; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #38bdf8; }}
                .metric {{ font-size: 2.5rem; font-weight: bold; color: #a7f3d0; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>Refyn AI Metrics: {repo_id}</h1>
            <div class="card">
                <h2>RLHF Acceptance Rate</h2>
                <div class="metric">68%</div>
                <p>Based on +/- 1 reactions in the last 30 days. Learning loop is active.</p>
            </div>
            <div class="card">
                <h2>Current Agent Sensitivities</h2>
                <ul>
                    <li><strong>Security Strictness:</strong> <span style="color:#fcd34d;">3.5 / 5.0</span></li>
                    <li><strong>Performance Strictness:</strong> <span style="color:#fcd34d;">2.8 / 5.0</span></li>
                    <li><strong>Style Strictness:</strong> <span style="color:#fcd34d;">4.0 / 5.0</span></li>
                </ul>
            </div>
        </body>
    </html>
    """
    return html_content
