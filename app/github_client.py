"""GitHub REST API Client."""

import httpx
from typing import Any
from app.auth import get_installation_token
import structlog

logger = structlog.get_logger()

class GitHubClient:
    """Async client for interacting with the GitHub REST API."""
    
    def __init__(self, installation_id: int, repo_full_name: str):
        self.installation_id = installation_id
        self.repo_full_name = repo_full_name
        self.base_url = f"https://api.github.com/repos/{repo_full_name}"
        
    async def _get_client(self) -> httpx.AsyncClient:
        token = await get_installation_token(self.installation_id)
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff" # Default to diff for PRs
        }
        return httpx.AsyncClient(base_url=self.base_url, headers=headers)
        
    async def get_pr_diff(self, pr_number: int) -> str:
        """Fetch the unified diff of a pull request."""
        async with await self._get_client() as client:
            response = await client.get(f"/pulls/{pr_number}")
            response.raise_for_status()
            return response.text
            
    async def post_review_comment(self, pr_number: int, commit_id: str, file_path: str, line: int, body: str) -> dict[str, Any]:
        """Post an inline review comment on a specific line of a file in the PR."""
        async with await self._get_client() as client:
            client.headers["Accept"] = "application/vnd.github.v3+json"
            
            payload = {
                "body": body,
                "commit_id": commit_id,
                "path": file_path,
                "line": line,
                "side": "RIGHT" # Comment on the new code side
            }
            
            response = await client.post(f"/pulls/{pr_number}/comments", json=payload)
            response.raise_for_status()
            return response.json()
