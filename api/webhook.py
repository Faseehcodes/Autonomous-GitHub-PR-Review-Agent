from fastapi import APIRouter, BackgroundTasks, Request

from agent.graph import run_review_agent
from services.github_service import verify_webhook_signature

router = APIRouter()


@router.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks) -> dict[str, str]:
    payload = await verify_webhook_signature(request)
    event = request.headers.get("X-GitHub-Event")

    if event == "ping":
        return {"status": "pong"}

    if event != "pull_request":
        return {"status": "ignored", "reason": "unsupported_event"}

    if payload.get("action") not in {"opened", "synchronize", "reopened"}:
        return {"status": "ignored", "reason": "unsupported_action"}

    background_tasks.add_task(run_review_agent, payload)
    return {"status": "review_queued"}
