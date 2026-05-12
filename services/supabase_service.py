import os
from typing import Any

import httpx

from agent.state import PRReviewState


class SupabaseService:
    def __init__(self) -> None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY are not configured")

        self.url = url.rstrip("/")
        self.key = key
        self.rest_url = f"{self.url}/rest/v1"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    @classmethod
    def is_configured(cls) -> bool:
        return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY"))

    def list_repositories(self) -> list[dict[str, Any]]:
        return self._request(
            "GET",
            "/repositories",
            params={"select": "*", "order": "created_at.desc"},
        )

    def list_reviews(self) -> list[dict[str, Any]]:
        return self._request(
            "GET",
            "/reviews",
            params={"select": "*", "order": "created_at.desc", "limit": "50"},
        )

    def get_review_by_pr(self, pr_id: int) -> dict[str, Any]:
        reviews = self._request(
            "GET",
            "/reviews",
            params={
                "select": "*",
                "pr_number": f"eq.{pr_id}",
                "order": "created_at.desc",
                "limit": "1",
            },
        )
        review = (reviews or [None])[0]
        if not review:
            return {"pr_id": pr_id, "comments": []}

        review["comments"] = self._request(
            "GET",
            "/review_comments",
            params={"select": "*", "review_id": f"eq.{review['id']}", "order": "file_path.asc"},
        )
        return review

    def save_review(self, state: PRReviewState) -> None:
        repo = self._upsert_repository(state["repo_full_name"])
        comments = state.get("final_comments", [])

        review_payload = {
            "repo_id": repo["id"],
            "repo_full_name": state["repo_full_name"],
            "pr_number": state["pr_number"],
            "pr_title": state.get("pr_title", ""),
            "pr_author": state.get("pr_author", ""),
            "quality_score": state.get("quality_score", 80),
            "total_comments": len(comments),
            "bugs_found": sum(1 for item in comments if item.get("issue_type") == "bug"),
            "security_issues": sum(1 for item in comments if item.get("issue_type") == "security"),
            "status": "completed" if state.get("posted") else "failed",
            "summary": state.get("summary", ""),
        }

        review_response = self._request("POST", "/reviews", json=review_payload, prefer_return=True)
        review = (review_response or [None])[0]
        if not review:
            return

        comment_payloads = [
            {
                "review_id": review["id"],
                "file_path": comment.get("file_path", ""),
                "line_number": int(comment.get("line_number", 0) or 0),
                "issue_type": comment.get("issue_type", "quality"),
                "severity": comment.get("severity", "minor"),
                "comment_body": comment.get("comment_body", ""),
                "suggestion": comment.get("suggestion", ""),
            }
            for comment in comments
        ]
        if comment_payloads:
            self._request("POST", "/review_comments", json=comment_payloads)

    def _upsert_repository(self, repo_full_name: str) -> dict[str, Any]:
        payload = {
            "full_name": repo_full_name,
            "config": {"strictness": "medium", "languages": ["python", "javascript", "typescript"]},
        }
        response = self._request(
            "POST",
            "/repositories",
            params={"on_conflict": "full_name"},
            json=payload,
            extra_headers={"Prefer": "resolution=merge-duplicates,return=representation"},
        )
        return response[0]

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json: Any | None = None,
        prefer_return: bool = False,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        headers = dict(self.headers)
        if prefer_return:
            headers["Prefer"] = "return=representation"
        if extra_headers:
            headers.update(extra_headers)

        with httpx.Client(timeout=30) as client:
            response = client.request(
                method,
                f"{self.rest_url}{path}",
                headers=headers,
                params=params,
                json=json,
            )

        if response.status_code >= 400:
            raise RuntimeError(f"{response.status_code} {response.text}")
        if not response.content:
            return []
        return response.json()
