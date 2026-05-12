from pydantic import BaseModel, Field


class ReviewComment(BaseModel):
    file_path: str
    line_number: int
    issue_type: str
    severity: str = Field(pattern="^(critical|major|minor)$")
    comment_body: str
    suggestion: str = ""


class ReviewSummary(BaseModel):
    pr_number: int
    repo_full_name: str
    quality_score: int
    summary: str
    comments: list[ReviewComment]
