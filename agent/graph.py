from langgraph.graph import END, StateGraph

from agent.nodes.analyze import analyze_node
from agent.nodes.commenter import post_comments_node
from agent.nodes.security import security_node
from agent.nodes.triage import triage_node
from agent.state import PRReviewState


def _after_triage(state: PRReviewState) -> str:
    return "skip" if state.get("triage_result") == "trivial" else "continue"


def build_agent():
    graph = StateGraph(PRReviewState)

    graph.add_node("triage", triage_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("security", security_node)
    graph.add_node("post_comments", post_comments_node)

    graph.set_entry_point("triage")
    graph.add_conditional_edges(
        "triage",
        _after_triage,
        {"skip": "post_comments", "continue": "analyze"},
    )
    graph.add_edge("analyze", "security")
    graph.add_edge("security", "post_comments")
    graph.add_edge("post_comments", END)

    return graph.compile()


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

    agent = build_agent()
    return await agent.ainvoke(initial_state)
