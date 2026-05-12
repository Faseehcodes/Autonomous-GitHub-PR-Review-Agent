from agent.state import PRReviewState
from services.llm_service import GroqReviewClient


async def analyze_node(state: PRReviewState) -> PRReviewState:
    client = GroqReviewClient()
    comments = []

    for chunk in state.get("diff_chunks", []):
        result = await client.review_diff_chunk(chunk)
        comments.extend(result.get("comments", []))

    state["analysis_comments"] = comments
    return state
