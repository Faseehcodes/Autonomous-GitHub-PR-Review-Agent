from pydantic import BaseModel, Field


class RepositoryConfig(BaseModel):
    strictness: str = "medium"
    languages: list[str] = Field(default_factory=lambda: ["python", "javascript", "typescript"])


class Repository(BaseModel):
    id: str
    full_name: str
    webhook_id: int | None = None
    config: RepositoryConfig = Field(default_factory=RepositoryConfig)
