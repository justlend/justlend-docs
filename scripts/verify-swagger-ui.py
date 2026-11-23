"""Verify the published Swagger UI offline, or audit the locked distribution online."""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hooks"))
from omit_source_maps import without_source_map

DIST = ROOT / "node_modules/swagger-ui-dist"
BUNDLES = {"swagger-ui-bundle.js", "swagger-ui-standalone-preset.js"}


def local_asset(site, page, url):
    parts = urlsplit(url)
    path = unquote(parts.path)
    target = ((site if path.startswith("/") else page.parent) / path.lstrip("/")).resolve()
    if parts.scheme or parts.netloc or not target.is_relative_to(site) or not target.is_file():
        sys.exit(f"Expected a published local asset: {page.name} → {url}")
    return target


def locked_version():
    lock = json.loads((ROOT / "package-lock.json").read_text())
    version = lock["packages"]["node_modules/swagger-ui-dist"]["version"]
    if json.loads((DIST / "package.json").read_text())["version"] != version:
        sys.exit("Swagger UI installation does not match package-lock.json; run npm ci --ignore-scripts.")
    return version


def verify(site, version):
    from bs4 import BeautifulSoup  # Only the offline HTML check needs the docs build environment.

    site = site.resolve()
    page = site / "developers/apis/index.html"
    iframe = BeautifulSoup(page.read_bytes(), "html.parser").select_one("iframe.swagger-ui-iframe[src]")
    if not iframe:
        sys.exit("The API reference has no Swagger UI iframe.")
    frame = local_asset(site, page, iframe["src"])
    scripts = BeautifulSoup(frame.read_bytes(), "html.parser").select("script[src]")
    published = [local_asset(site, frame, tag["src"]) for tag in scripts]
    if sorted(asset.name for asset in published) != sorted(BUNDLES):
        sys.exit(f"Unexpected Swagger UI scripts: {published}")
    for asset in published:
        expected = without_source_map((DIST / asset.name).read_bytes(), asset.name)
        if asset.read_bytes() != expected:
            sys.exit(f"{asset.name}: published JS differs from locked swagger-ui-dist {version}")
    print(f"Swagger UI {version}: both local scripts match the locked release (excluding terminal map directives).")


def fetch_json(url, payload=None):
    import requests  # Only the independent online scan needs an HTTP client.

    response = requests.get(url, timeout=30) if payload is None else requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def audit(version):
    # The publisher reused identical .js.map files across different JS releases.
    # Bind the lock to the build revision embedded in the actual shipped bundle instead.
    main_js = (DIST / "swagger-ui-bundle.js").read_bytes()
    build = re.search(rb'PACKAGE_VERSION:"([^"]+)",GIT_COMMIT:"g?([0-9a-f]{7,40})"', main_js)
    if not build or build[1].decode() != version:
        sys.exit("Cannot bind the published JS to the locked Swagger UI build.")
    revision = build[2].decode()
    lock_url = f"https://raw.githubusercontent.com/swagger-api/swagger-ui/{revision}/package-lock.json"
    packages = fetch_json(lock_url)["packages"]
    stats = (DIST / "log.bundle-sizes.swagger-ui.txt").read_text().splitlines()
    bundled = {line.partition(": ")[0] for line in stats if line and not line.startswith("<self>:")}
    targets = ("immutable", "js-yaml")
    if not bundled.issuperset(targets):
        sys.exit("The publisher's bundle inventory no longer identifies both security-sensitive dependencies.")

    # The publisher lists names, not versions. Include every locked version of a named
    # component, even dev-marked browser shims, but not unrelated upstream packages.
    versions = defaultdict(set)
    for path, package in packages.items():
        if "node_modules/" in path:
            name = path.rsplit("node_modules/", 1)[1]
            if name in bundled:
                versions[name].add(package["version"])
    if missing := bundled.difference(versions):
        sys.exit("Unresolved packages in the publisher's bundle inventory: " + ", ".join(sorted(missing)))

    versions["swagger-ui-dist"].add(version)
    report = fetch_json(
        "https://registry.npmjs.org/-/npm/v1/security/advisories/bulk",
        {name: sorted(found) for name, found in versions.items()},
    )
    alerts = [(name, alert) for name, group in report.items() if name in versions for alert in group]
    severe = [(name, alert) for name, alert in alerts if alert["severity"] in {"high", "critical"}]
    candidates = ", ".join(f"{name} {'/'.join(sorted(versions[name]))}" for name in targets)
    print(f"Swagger UI {version} ({revision}): {len(bundled)} named bundle components; "
          f"{len(severe)} High/Critical. Locked candidates: {candidates}.")
    for name, alert in alerts:
        print(f"{alert['severity']} {name}: {alert['url']}")
    if severe:
        sys.exit("High/Critical advisories remain in the checked dependency set.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("site", nargs="?", type=Path, help="verify the built site offline (default: site)")
    mode.add_argument("--audit", action="store_true", help="query advisories for the locked npm distribution instead")
    args = parser.parse_args()
    if args.audit:
        audit(locked_version())
    else:
        verify(args.site or Path("site"), locked_version())
