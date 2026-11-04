"""Publish verified Swagger assets after the plugin copies its older bundles.

Offline check: python hooks/secure_swagger.py --site-dir site
Known-advisory check: add --audit (queries only public package names/versions).
No downloads occur during MkDocs builds, and integrity errors abort the build.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from mkdocs.plugins import event_priority

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "swagger-ui-bundle.js": "assets/javascripts/swagger-ui-bundle.js",
    "swagger-ui-bundle.js.map": "assets/javascripts/swagger-ui-bundle.js.map",
    "swagger-ui-bundle.js.LICENSE.txt": "assets/javascripts/swagger-ui-bundle.js.LICENSE.txt",
    "swagger-ui-standalone-preset.js": "assets/javascripts/swagger-ui-standalone-preset.js",
    "swagger-ui-standalone-preset.js.map": "assets/javascripts/swagger-ui-standalone-preset.js.map",
    "swagger-ui-standalone-preset.js.LICENSE.txt": "assets/javascripts/swagger-ui-standalone-preset.js.LICENSE.txt",
    "swagger-ui.css": "assets/stylesheets/swagger-ui.css",
    "swagger-ui.css.map": "assets/stylesheets/swagger-ui.css.map",
    "oauth2-redirect.html": "assets/swagger-ui/oauth2-redirect.html",
    "oauth2-redirect.js": "assets/swagger-ui/oauth2-redirect.js",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources(root: Path = ROOT) -> dict:
    vendor = (root / "vendor/swagger-ui").resolve()
    manifest = json.loads((vendor / "manifest.json").read_text())
    if set(manifest["packages"]) != {"swagger-ui-dist", "dompurify"}:
        raise ValueError("Unexpected browser package inventory")
    if set(manifest["assets"]) != set(ASSETS):
        raise ValueError("Swagger asset allowlist does not match manifest")
    for name in ASSETS:
        source = vendor / name
        if not source.resolve().is_relative_to(vendor):
            raise ValueError("Swagger source is outside vendor directory")
        if digest(source) != manifest["assets"][name]:
            raise ValueError(f"Swagger source hash mismatch: {name}")
    bundle = (vendor / "swagger-ui-bundle.js").read_text()
    versions = re.findall(r'DOMPurify.version\s*=\s*["\']([^"\']+)', bundle)
    if versions != [manifest["packages"]["dompurify"]]:
        raise ValueError("DOMPurify version does not match reviewed manifest")
    return manifest


def destination(site: Path, relative: str) -> Path:
    target = site / relative
    if not target.resolve().is_relative_to(site.resolve()):
        raise ValueError("Swagger output is outside site directory")
    # Do not follow a pre-existing file symlink, even one pointing inside site.
    if target.is_symlink():
        raise ValueError("Swagger output must not be a symlink")
    return target


def verify_site(root: Path, site: Path) -> None:
    manifest = verify_sources(root)
    for name, relative in ASSETS.items():
        if digest(destination(site, relative)) != manifest["assets"][name]:
            raise ValueError(f"Swagger published hash mismatch: {relative}")


def copy_assets(root: Path, site: Path) -> None:
    verify_sources(root)  # Validate every source before replacing any output.
    targets = {name: destination(site, relative) for name, relative in ASSETS.items()}
    for name, target in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        # Replace the entry, not the contents of a possible existing hardlink.
        temporary = target.with_name(target.name + ".verified-tmp")
        if temporary.exists() or temporary.is_symlink():
            raise ValueError("Unexpected temporary Swagger output")
        try:
            shutil.copyfile(root / "vendor/swagger-ui" / name, temporary)
            temporary.replace(target)
        finally:
            if temporary.exists():
                temporary.unlink()
    verify_site(root, site)


@event_priority(-100)
def on_post_build(config, **kwargs) -> None:
    copy_assets(ROOT, Path(config["site_dir"]))


def audit_packages(manifest: dict) -> list[dict]:
    import requests

    results = []
    for name, version in manifest["packages"].items():
        response = requests.post(
            "https://api.osv.dev/v1/query",
            json={"package": {"ecosystem": "npm", "name": name}, "version": version},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if (not isinstance(payload, dict)
                or (payload and "vulns" not in payload)
                or ("vulns" in payload and not isinstance(payload["vulns"], list))):
            raise ValueError("Invalid OSV response; cannot infer a clean result")
        results.append({"package": name, "version": version,
                        "advisories": [v["id"] for v in payload.get("vulns", [])]})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    manifest = verify_sources()
    if args.site_dir is not None:
        verify_site(ROOT, args.site_dir)
    if args.audit:
        results = audit_packages(manifest)
        print(json.dumps(results, indent=2))
        if any(row["advisories"] for row in results):
            raise SystemExit("Known browser dependency advisories remain")
    else:
        print("Verified Swagger source" + (" and published assets" if args.site_dir else ""))


if __name__ == "__main__":
    main()
