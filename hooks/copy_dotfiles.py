"""MkDocs hooks: dotfile mirroring + AI-snapshot metadata substitution.

This module installs two `on_post_build` actions:

1. **Dotfile publishing.** MkDocs intentionally skips dotfile directories
   (anything starting with `.`) during the build pass. We need
   `docs/.well-known/security.txt` and any future dotfile-rooted resources
   (`/.well-known/ai-plugin.json`, OIDC config, …) to be published verbatim
   under the site root. This hook walks every `docs/.<dir>/` tree, mirrors it
   into `site/.<dir>/`, and writes `site/.nojekyll` so GitHub Pages serves
   those directories instead of dropping them during Jekyll processing.

2. **Snapshot metadata substitution.** `docs/llms-full.txt §0` contains
   `{{LAST_GENERATED}}`, `{{DOCS_COMMIT}}`, and `{{DOCS_COMMIT_SHORT}}`
   placeholders. We replace them with the current build date and the
   current `git rev-parse HEAD` so the snapshot header always reflects
   the commit it was actually built from, instead of drifting because
   someone forgot to hand-edit the §0 block.

Mentioned in mkdocs.yml under `hooks:`.
"""

from __future__ import annotations

import datetime as _dt
import shutil
import subprocess
from pathlib import Path


def _copy_dotfile_dirs(docs_dir: Path, site_dir: Path) -> None:
    for src in docs_dir.iterdir():
        if not src.is_dir() or not src.name.startswith("."):
            continue
        dest = site_dir / src.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print(f"[copy_dotfiles] {src.relative_to(docs_dir)} -> {dest.relative_to(site_dir.parent)}")

    # Without this marker GitHub Pages runs Jekyll and excludes directories
    # whose names start with a dot, even though they exist on gh-pages.
    (site_dir / ".nojekyll").touch()


def _current_git_sha(repo_root: Path) -> str:
    """Resolve the current commit SHA. Prefer `git rev-parse HEAD`; fall back
    to the `GITHUB_SHA` env var (set in GitHub Actions); fall back to `unknown`.
    """
    import os

    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return os.environ.get("GITHUB_SHA", "unknown")


def _substitute_snapshot_metadata(site_dir: Path, repo_root: Path) -> None:
    target = site_dir / "llms-full.txt"
    if not target.exists():
        return

    sha = _current_git_sha(repo_root)
    short = sha[:7] if sha != "unknown" else "unknown"
    date = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")

    text = target.read_text()
    replaced = (
        text.replace("{{DOCS_COMMIT_SHORT}}", short)
            .replace("{{DOCS_COMMIT}}", sha)
            .replace("{{LAST_GENERATED}}", date)
    )
    if replaced != text:
        target.write_text(replaced)
        print(f"[snapshot_metadata] llms-full.txt: last_generated={date} docs_commit={short}")


def on_post_build(config, **kwargs) -> None:
    docs_dir = Path(config["docs_dir"])
    site_dir = Path(config["site_dir"])
    repo_root = docs_dir.parent

    _copy_dotfile_dirs(docs_dir, site_dir)
    _substitute_snapshot_metadata(site_dir, repo_root)
