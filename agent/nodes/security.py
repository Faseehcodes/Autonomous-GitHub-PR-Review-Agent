from agent.state import PRReviewState
from services.llm_service import GroqReviewClient


async def security_node(state: PRReviewState) -> PRReviewState:
    client = GroqReviewClient()
    result = await client.security_review(state["diff"])
    security_flags = result.get("comments", [])

    merged = [*state.get("analysis_comments", []), *security_flags]
    state["security_flags"] = security_flags
    state["final_comments"] = _dedupe_comments(merged)
    state["summary"] = result.get("summary") or state.get("summary", "")
    state["quality_score"] = min(
        int(state.get("quality_score", 80)),
        int(result.get("quality_score", state.get("quality_score", 80))),
    )

    return state


def _dedupe_comments(comments: list[dict]) -> list[dict]:
    seen = set()
    unique = []

    for comment in comments:
        key = (
            comment.get("file_path"),
            comment.get("line_number"),
            comment.get("issue_type"),
            comment.get("comment_body"),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(comment)

    return unique
