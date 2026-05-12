import re

MAX_SINGLE_CHUNK_CHARS = 50_000
SKIPPED_FILE_PATTERNS = (
    re.compile(r"(^|/)(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|poetry\.lock)$"),
    re.compile(r"(^|/)migrations?/"),
    re.compile(r"\.min\.(js|css)$"),
    re.compile(r"\.(png|jpe?g|gif|webp|ico|pdf|zip)$"),
)


def split_diff(diff: str) -> list[str]:
    if len(diff) < MAX_SINGLE_CHUNK_CHARS:
        return [diff] if diff.strip() else []

    chunks = []
    current_file = []

    for line in diff.splitlines(keepends=True):
        if line.startswith("diff --git ") and current_file:
            chunk = "".join(current_file)
            if not _should_skip_chunk(chunk):
                chunks.append(chunk)
            current_file = []
        current_file.append(line)

    if current_file:
        chunk = "".join(current_file)
        if not _should_skip_chunk(chunk):
            chunks.append(chunk)

    return chunks


def _should_skip_chunk(chunk: str) -> bool:
    first_line = chunk.splitlines()[0] if chunk else ""
    match = re.search(r" b/(.+)$", first_line)
    path = match.group(1) if match else first_line

    return any(pattern.search(path) for pattern in SKIPPED_FILE_PATTERNS)
