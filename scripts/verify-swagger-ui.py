"""Verify the Swagger bundles loaded by the API page and audit their identifiable npm components."""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "node_modules/swagger-ui-dist"
BUNDLES = {"swagger-ui-bundle.js", "swagger-ui-standalone-preset.js"}


def local_asset(site, page, url):
    parts = urlsplit(url)
    path = unquote(parts.path)
    target = ((site if path.startswith("/") else page.parent) / path.lstrip("/")).resolve()
    if parts.scheme or parts.netloc or not target.is_relative_to(site) or not target.is_file():
        sys.exit(f"Expected a published local asset: {page.name} → {url}")
    return target


def verify(site):
    lock = json.loads((ROOT / "package-lock.json").read_text())
    version = lock["packages"]["node_modules/swagger-ui-dist"]["version"]
    if json.loads((DIST / "package.json").read_text())["version"] != version:
        sys.exit("Swagger UI installation does not match package-lock.json; run npm ci --ignore-scripts.")

    page = site / "developers/apis/index.html"
    iframe = BeautifulSoup(page.read_bytes(), "html.parser").select_one("iframe.swagger-ui-iframe[src]")
    if not iframe:
        sys.exit("The API reference has no Swagger UI iframe.")
    frame = local_asset(site, page, iframe["src"])
    scripts = BeautifulSoup(frame.read_bytes(), "html.parser").select("script[src]")
    published = [local_asset(site, frame, tag["src"]) for tag in scripts]
    if {asset.name for asset in published} != BUNDLES:
        sys.exit(f"Unexpected Swagger UI scripts: {published}")
    for asset in published:
        if asset.read_bytes() != (DIST / asset.name).read_bytes():
            sys.exit(f"{asset.name}: published JS differs from locked swagger-ui-dist {version}")

    # The publisher reused identical .js.map files across different JS releases.
    # Bind the lock to the build revision embedded in the actual shipped bundle instead.
    main_js = (DIST / "swagger-ui-bundle.js").read_bytes()
    build = re.search(rb'PACKAGE_VERSION:"([^"]+)",GIT_COMMIT:"g?([0-9a-f]{7,40})"', main_js)
    if not build or build[1].decode() != version:
        sys.exit("Cannot bind the published JS to the locked Swagger UI build.")
    revision = build[2].decode()
    source = requests.get(
        f"https://raw.githubusercontent.com/swagger-api/swagger-ui/{revision}/package-lock.json", timeout=30
    )
    source.raise_for_status()
    packages = source.json()["packages"]
    stats = (DIST / "log.bundle-sizes.swagger-ui.txt").read_text().splitlines()
    bundled = {line.partition(": ")[0] for line in stats if line and not line.startswith("<self>:")}
    targets = ("immutable", "js-yaml")
    if not bundled.issuperset(targets):
        sys.exit("The publisher's bundle inventory no longer identifies both security-sensitive dependencies.")

    # Audit a conservative superset: all runtime deps plus every locked version of a
    # package reported by the bundler (some browser shims are marked dev-only upstream).
    versions = defaultdict(set)
    for path, package in packages.items():
        if "node_modules/" in path:
            name = path.rsplit("node_modules/", 1)[1]
            if not package.get("dev") or name in bundled:
                versions[name].add(package["version"])
    if missing := bundled.difference(versions):
        sys.exit("Unresolved packages in the publisher's bundle inventory: " + ", ".join(sorted(missing)))

    versions["swagger-ui-dist"].add(version)
    report = requests.post(
        "https://registry.npmjs.org/-/npm/v1/security/advisories/bulk",
        json={name: sorted(found) for name, found in versions.items()}, timeout=30,
    )
    report.raise_for_status()
    alerts = [(name, alert) for name, group in report.json().items() for alert in group]
    severe = [(name, alert) for name, alert in alerts if alert["severity"] in {"high", "critical"}]
    direct = ", ".join(f"{name} {packages['node_modules/' + name]['version']}" for name in targets)
    print(f"Swagger UI {version} ({revision}): both published bundles match; {direct}. "
          f"{len(bundled)} bundled package names accounted for; {len(severe)} High/Critical.")
    for name, alert in alerts:
        scope = "bundle inventory" if name in bundled else "upstream dependency tree only"
        print(f"{alert['severity']} {name} ({scope}): {alert['url']}")
    if severe:
        sys.exit("High/Critical advisories remain in the checked dependency set.")


if __name__ == "__main__":
    verify(Path(sys.argv[1] if len(sys.argv) > 1 else "site").resolve())
