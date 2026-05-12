from fastapi import APIRouter, HTTPException

from services.supabase_service import SupabaseService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("")
async def list_reviews() -> dict[str, list]:
    if not SupabaseService.is_configured():
        return {"reviews": []}

    try:
        return {"reviews": SupabaseService().list_reviews()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Supabase error: {exc}") from exc


@router.get("/{pr_id}")
async def get_review(pr_id: int) -> dict[str, int | list]:
    if not SupabaseService.is_configured():
        return {"pr_id": pr_id, "comments": []}

    try:
        return SupabaseService().get_review_by_pr(pr_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Supabase error: {exc}") from exc
