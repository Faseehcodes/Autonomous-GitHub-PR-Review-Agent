from typing import Any, TypedDict


class PRReviewState(TypedDict, total=False):
    pr_number: int
    repo_full_name: str
    pr_title: str
    pr_author: str
    head_sha: str
    diff: str
    diff_chunks: list[str]
    triage_result: str
    analysis_comments: list[dict[str, Any]]
    security_flags: list[dict[str, Any]]
    final_comments: list[dict[str, Any]]
    summary: str
    quality_score: int
    posted: bool
    skipped_reason: str
