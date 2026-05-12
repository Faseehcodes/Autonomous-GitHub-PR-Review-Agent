import json
import os
from typing import Any

import httpx


class GroqReviewClient:
    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")

        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.triage_model = os.getenv("GROQ_TRIAGE_MODEL", "llama-3.1-8b-instant")
        self.analysis_model = os.getenv("GROQ_ANALYSIS_MODEL", "llama-3.3-70b-versatile")
        self.security_model = os.getenv("GROQ_SECURITY_MODEL", "llama-3.3-70b-versatile")

    async def triage_diff(self, diff: str) -> dict[str, Any]:
        return await self._json_chat(
            model=self.triage_model,
            system=(
                "You are a senior code reviewer. Classify the PR diff as trivial, standard, or complex. "
                "Trivial means docs-only, formatting-only, comments-only, or tiny placeholder text changes. "
                "Return only JSON with keys triage_result, reason, summary, quality_score."
            ),
            user=f"Review this PR diff for triage:\n\n{diff[:40_000]}",
        )

    async def review_diff_chunk(self, diff_chunk: str) -> dict[str, Any]:
        return await self._json_chat(
            model=self.analysis_model,
            system=_review_system_prompt(),
            user=f"Review this diff chunk:\n\n{diff_chunk}",
        )

    async def security_review(self, diff: str) -> dict[str, Any]:
        return await self._json_chat(
            model=self.security_model,
            system=(
                "You are a security-focused code reviewer. Find only concrete, exploitable security risks in the diff. "
                "Do not label random placeholder text, nonsense text, README edits, or normal docs changes as security issues. "
                "If no real security issue exists, return an empty comments array. "
                "Return strict JSON with keys comments, summary, quality_score. "
                "Each comment must contain file_path, line_number, issue_type, severity, comment_body, suggestion."
            ),
            user=f"Run a security review on this PR diff:\n\n{diff[:70_000]}",
        )

    async def _json_chat(self, model: str, system: str, user: str) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)


def _review_system_prompt() -> str:
    return (
        "You are a senior engineer reviewing a GitHub PR. Find bugs, logic errors, security issues, "
        "performance problems, and missing tests. Return strict JSON with a comments array. Each comment "
        "must contain file_path, line_number, issue_type, severity, comment_body, suggestion. "
        "Allowed issue_type values are bug, security, quality, performance, test_coverage, documentation. "
        "Allowed severity values are critical, major, minor. "
        "Use critical only for production-breaking bugs, data loss, or exploitable vulnerabilities. "
        "Use major for likely bugs or serious maintainability problems. "
        "Use minor for docs mistakes, placeholder text, naming, style, or small cleanup. "
        "Do not call placeholder text a security issue unless it contains real secrets, credentials, tokens, PII, "
        "private keys, connection strings, or exploitable examples. "
        "For README/docs placeholder text, use issue_type documentation or quality and severity minor. "
        "Use line_number from the new side of the diff whenever possible. Only report actionable issues. "
        "If the diff has no useful issue, return {\"comments\": []}."
    )
