"""MkDocs hook: copy dotfile directories from docs/ into the build output.

MkDocs intentionally ignores dotfile directories (anything starting with `.`)
during the build pass. We need `docs/.well-known/security.txt` and any future
dotfile-rooted resources (e.g., `/.well-known/ai-plugin.json`, OIDC config)
to be published verbatim under the site root.

This hook runs after `mkdocs build` finishes copying regular files, walks every
`docs/.<dir>/` tree, and mirrors its contents into `site/.<dir>/`.

Mentioned in mkdocs.yml under `hooks:`.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def on_post_build(config, **kwargs) -> None:
    docs_dir = Path(config["docs_dir"])
    site_dir = Path(config["site_dir"])

    for src in docs_dir.iterdir():
        if not src.is_dir() or not src.name.startswith("."):
            continue
        dest = site_dir / src.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print(f"[copy_dotfiles] {src.relative_to(docs_dir)} -> {dest.relative_to(site_dir.parent)}")
