#!/usr/bin/env python3
"""Merge MT6893 compatibility patches onto updated upstream branches."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

IDENTITY = ["-c", "user.name=MT6893 PixelOS patches", "-c",
            "user.email=63958697+seriaTvT@users.noreply.github.com"]
ENV = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0")


def git(project, *command, extra_env=None, check=True):
    return subprocess.run(
        ["git", "-C", str(project), *command],
        env=dict(ENV, **(extra_env or {})), capture_output=True, text=True,
        check=check,
    )


def value(project, *command, **kwargs):
    return git(project, *command, **kwargs).stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify patches are present without changing checked-out files")
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.root.resolve()
    patches = Path(__file__).resolve().parent
    pending = []

    # Preflight every repository before changing any worktree or real index.
    for item in json.loads((patches / "series.json").read_text()):
        project = root / item["project"]
        patch = patches / "series" / item["patch"]
        if hashlib.sha256(patch.read_bytes()).hexdigest() != item["sha256"]:
            raise SystemExit("Patch hash mismatch: " + item["project"])
        if value(project, "status", "--porcelain"):
            raise SystemExit("Commit or stash local changes first: " + item["project"])
        head = value(project, "rev-parse", "HEAD")
        current_tree = value(project, "rev-parse", "HEAD^{tree}")
        if current_tree == item["tree"]:
            print("Verified:", item["project"], flush=True)
            continue
        if git(project, "merge-base", "--is-ancestor", item["base"], head,
               check=False).returncode:
            raise SystemExit("Missing base history or upstream was rewritten; "
                             "fetch complete history and review the port: " + item["project"])

        # Reconstruct and verify the original patch independently of upstream.
        with tempfile.TemporaryDirectory(prefix="pixelos-patch-") as temporary:
            index_env = {"GIT_INDEX_FILE": str(Path(temporary) / "index")}
            git(project, "read-tree", item["base"], extra_env=index_env)
            git(project, "apply", "--cached", str(patch), extra_env=index_env)
            patched_tree = value(project, "write-tree", extra_env=index_env)
        if patched_tree != item["tree"]:
            raise SystemExit("Unexpected original patch tree: " + item["project"])

        # A stable, unattached commit supplies the patch side of the merge.
        merge_commit = value(
            project, *IDENTITY, "commit-tree", patched_tree, "-p", item["base"],
            "-m", "MT6893 compatibility merge input: " + item["sha256"],
            extra_env={"GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000",
                       "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000"},
        )
        merged = git(project, "merge-tree", "--write-tree", "--merge-base",
                     item["base"], head, merge_commit, check=False)
        if merged.returncode:
            raise SystemExit("Three-way merge failed; no worktrees were changed. "
                             "Review this patch against upstream: " + item["project"]
                             + "\n" + merged.stdout + merged.stderr)
        target_tree = merged.stdout.splitlines()[0]
        if target_tree == current_tree:
            print("Verified:", item["project"], flush=True)
        else:
            pending.append((item, project, head, target_tree))

    if args.check and pending:
        raise SystemExit("Patches need application: "
                         + ", ".join(item["project"] for item, *_ in pending))

    for item, project, head, target_tree in pending:
        if value(project, "rev-parse", "HEAD") != head or value(project, "status", "--porcelain"):
            raise SystemExit("Source changed during preflight; rerun: " + item["project"])
        # A two-tree checkout refuses untracked files that would be overwritten.
        git(project, "read-tree", "-u", "-m", head, target_tree)
        git(project, *IDENTITY, "commit", "-m",
            "Apply MT6893 compatibility to updated upstream: " + item["project"],
            "-m", "PixelOS-Patch-SHA256: " + item["sha256"])
        if value(project, "rev-parse", "HEAD^{tree}") != target_tree:
            raise SystemExit("Unexpected committed tree; inspect: " + item["project"])
        print("Applied:", item["project"], flush=True)

    print("All compatibility patches verified against the current source trees.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.stderr or error.stdout or str(error)) from None
