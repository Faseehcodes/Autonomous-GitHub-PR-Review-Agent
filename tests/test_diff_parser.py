from services.diff_parser import split_diff


def test_split_diff_returns_single_small_chunk():
    diff = "diff --git a/app.py b/app.py\n+print('hello')\n"

    assert split_diff(diff) == [diff]


def test_split_diff_skips_lock_files_when_chunking():
    large_header = "diff --git a/package-lock.json b/package-lock.json\n"
    large_lock = large_header + ("+x\n" * 30_000)
    app_diff = "diff --git a/app.py b/app.py\n+print('ok')\n"

    chunks = split_diff(large_lock + app_diff)

    assert chunks == [app_diff]
