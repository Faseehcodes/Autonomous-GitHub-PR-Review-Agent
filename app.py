from fastapi import FastAPI
from dotenv import load_dotenv

from api.repos import router as repos_router
from api.reviews import router as reviews_router
from api.webhook import router as webhook_router

load_dotenv()

app = FastAPI(title="Autonomous PR Review Agent", version="0.1.0")

app.include_router(webhook_router)
app.include_router(repos_router)
app.include_router(reviews_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
