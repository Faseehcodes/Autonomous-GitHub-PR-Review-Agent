from agent.state import PRReviewState
from services.github_service import GitHubService
from services.supabase_service import SupabaseService


async def post_comments_node(state: PRReviewState) -> PRReviewState:
    github = GitHubService()

    if state.get("triage_result") == "trivial":
        body = (
            "## AI PR Review\n\n"
            f"No blocking issues found. Skipped deep review: {state.get('skipped_reason', 'trivial diff')}."
        )
        await github.post_summary_comment(state["repo_full_name"], state["pr_number"], body)
        state["posted"] = True
        _save_review_if_configured(state)
        return state

    final_comments = state.get("final_comments", [])
    posting_errors = []
    for comment in final_comments:
        try:
            await github.post_inline_comment(
                repo_full_name=state["repo_full_name"],
                pr_number=state["pr_number"],
                commit_id=state["head_sha"],
                file_path=comment["file_path"],
                line_number=int(comment["line_number"]),
                body=_format_inline_comment(comment),
            )
        except Exception as exc:
            posting_errors.append(
                f"- {comment.get('file_path')}:{comment.get('line_number')} could not be posted inline: {exc}"
            )

    await github.post_summary_comment(
        state["repo_full_name"],
        state["pr_number"],
        _format_summary(state, posting_errors),
    )
    state["posted"] = True
    _save_review_if_configured(state)
    return state


def _format_inline_comment(comment: dict) -> str:
    parts = [
        f"**{comment.get('severity', 'minor').title()} {comment.get('issue_type', 'quality')} issue**",
        "",
        str(comment.get("comment_body", "")).strip(),
    ]

    suggestion = str(comment.get("suggestion", "")).strip()
    if suggestion:
        parts.extend(["", "Suggested fix:", "```suggestion", suggestion, "```"])

    return "\n".join(parts)


def _format_summary(state: PRReviewState, posting_errors: list[str] | None = None) -> str:
    comments = state.get("final_comments", [])
    severity_counts = {
        "critical": sum(1 for item in comments if item.get("severity") == "critical"),
        "major": sum(1 for item in comments if item.get("severity") == "major"),
        "minor": sum(1 for item in comments if item.get("severity") == "minor"),
    }

    recommendation = "request changes" if severity_counts["critical"] or severity_counts["major"] else "needs discussion"
    if not comments:
        recommendation = "approve"

    body = (
        "## AI PR Review\n\n"
        f"**Quality score:** {state.get('quality_score', 80)}/100\n\n"
        f"**Recommendation:** {recommendation}\n\n"
        f"**Issues:** {len(comments)} total "
        f"({severity_counts['critical']} critical, {severity_counts['major']} major, {severity_counts['minor']} minor)\n\n"
        f"{state.get('summary', 'Review completed.')}"
    )

    if posting_errors:
        body += "\n\n**Inline posting warnings:**\n" + "\n".join(posting_errors[:5])

    return body


def _save_review_if_configured(state: PRReviewState) -> None:
    if not SupabaseService.is_configured():
        return

    try:
        SupabaseService().save_review(state)
    except Exception as exc:
        print(f"Supabase save failed: {exc}")
