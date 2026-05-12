from agent.state import PRReviewState
from services.llm_service import GroqReviewClient


async def triage_node(state: PRReviewState) -> PRReviewState:
    client = GroqReviewClient()
    result = await client.triage_diff(state["diff"])

    state["triage_result"] = result.get("triage_result", "standard")
    state["summary"] = result.get("summary", "")
    state["quality_score"] = int(result.get("quality_score", 80))

    if state["triage_result"] == "trivial":
        state["skipped_reason"] = result.get("reason", "Diff appears trivial.")
        state["final_comments"] = []

    return state
