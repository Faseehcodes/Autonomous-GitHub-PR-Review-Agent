import hashlib
import hmac
import os

import httpx
from fastapi import HTTPException, Request
from github import Github


async def verify_webhook_signature(request: Request) -> dict:
    secret = os.getenv("GITHUB_APP_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="GITHUB_APP_SECRET is not configured")

    body = await request.body()
    signature_header = request.headers.get("X-Hub-Signature-256", "")
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature_header, expected):
        raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature")

    return await request.json()


class GitHubService:
    def __init__(self) -> None:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise RuntimeError("GITHUB_TOKEN is not configured")
        self.token = token
        self.client = Github(token)

    async def fetch_pull_request_diff(self, repo_full_name: str, pr_number: int) -> str:
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
        headers = {
            "Accept": "application/vnd.github.v3.diff",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text

    async def post_inline_comment(
        self,
        repo_full_name: str,
        pr_number: int,
        commit_id: str,
        file_path: str,
        line_number: int,
        body: str,
    ) -> None:
        repo = self.client.get_repo(repo_full_name)
        pull = repo.get_pull(pr_number)
        pull.create_review_comment(
            body=body,
            commit=repo.get_commit(commit_id),
            path=file_path,
            line=line_number,
            side="RIGHT",
        )

    async def post_summary_comment(self, repo_full_name: str, pr_number: int, body: str) -> None:
        repo = self.client.get_repo(repo_full_name)
        pull = repo.get_pull(pr_number)
        pull.create_issue_comment(body)
