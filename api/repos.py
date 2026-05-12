from fastapi import APIRouter, HTTPException

from services.supabase_service import SupabaseService

router = APIRouter(prefix="/repos", tags=["repos"])


@router.get("")
async def list_repos() -> dict[str, list]:
    if not SupabaseService.is_configured():
        return {"repositories": []}

    try:
        return {"repositories": SupabaseService().list_repositories()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Supabase error: {exc}") from exc
