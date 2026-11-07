"""Local git ancestry: evidence of commit inclusion, not proof of accessibility."""
from pathlib import Path
import subprocess


def commit_in_ref(repo, commit, ref):
    root = Path(repo)
    if not (root / ".git").exists():
        raise ValueError("Expected a local .git checkout")
    for rev in (commit, ref):
        check = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--end-of-options", rev], capture_output=True, text=True, check=False)
        if check.returncode != 0:
            raise ValueError(f"Cannot resolve Git revision: {rev}")
    check = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit, ref], capture_output=True, check=False)
    if check.returncode not in (0, 1):
        raise RuntimeError(check.stderr.decode("utf-8", "replace") if isinstance(check.stderr, bytes) else check.stderr)
    return {"commit": commit, "ref": ref, "included": check.returncode == 0,
            "caution": "Commit inclusion is not proof of corrected accessibility behavior; cherry-picks need separate investigation."}
