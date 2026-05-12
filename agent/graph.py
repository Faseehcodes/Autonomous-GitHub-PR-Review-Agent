from agent.nodes.analyze import analyze_node
from agent.nodes.commenter import post_comments_node
from agent.nodes.security import security_node
from agent.nodes.triage import triage_node
from agent.state import PRReviewState


async def run_review_agent(payload: dict) -> PRReviewState:
    from services.diff_parser import split_diff
    from services.github_service import GitHubService

    pull_request = payload["pull_request"]
    repo_full_name = payload["repository"]["full_name"]
    pr_number = pull_request["number"]

    github = GitHubService()
    diff = await github.fetch_pull_request_diff(repo_full_name, pr_number)

    initial_state: PRReviewState = {
        "pr_number": pr_number,
        "repo_full_name": repo_full_name,
        "pr_title": pull_request.get("title", ""),
        "pr_author": pull_request.get("user", {}).get("login", ""),
        "head_sha": pull_request.get("head", {}).get("sha", ""),
        "diff": diff,
        "diff_chunks": split_diff(diff),
        "analysis_comments": [],
        "security_flags": [],
        "final_comments": [],
        "posted": False,
    }

    state = await triage_node(initial_state)

    if state.get("triage_result") != "trivial":
        state = await analyze_node(state)
        state = await security_node(state)

    return await post_comments_node(state)
