"""Use the locked Swagger UI distribution, not the older copy bundled by the iframe plugin."""

import json
from pathlib import Path
from shutil import copyfile

from mkdocs.exceptions import ConfigurationError
from mkdocs.plugins import event_priority
from omit_source_maps import omit_source_maps


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "node_modules" / "swagger-ui-dist"
ASSETS = {
    "javascripts": (
        "swagger-ui-bundle.js", "swagger-ui-bundle.js.LICENSE.txt",
        "swagger-ui-standalone-preset.js", "swagger-ui-standalone-preset.js.LICENSE.txt",
    ),
    "stylesheets": ("swagger-ui.css",),
    "swagger-ui": ("oauth2-redirect.html", "oauth2-redirect.js", "LICENSE", "NOTICE"),
}


def on_config(config) -> None:
    """Fail before building any pages rather than silently serving the plugin's old JS."""
    lock = json.loads((ROOT / "package-lock.json").read_text())
    expected = lock["packages"]["node_modules/swagger-ui-dist"]["version"]
    manifest = DIST / "package.json"
    if (
        not manifest.is_file()
        or json.loads(manifest.read_text())["version"] != expected
        or any(not (DIST / name).is_file() for group in ASSETS.values() for name in group)
    ):
        raise ConfigurationError(f"Swagger UI {expected} is required: run npm ci --ignore-scripts before MkDocs.")


@event_priority(-100)  # Finalize assets after swagger-ui-tag copies its iframe and vendor files.
def on_post_build(*, config) -> None:
    assets = Path(config.site_dir) / "assets"
    for directory, names in ASSETS.items():
        target = assets / directory
        target.mkdir(parents=True, exist_ok=True)
        for name in names:
            copyfile(DIST / name, target / name)
    omit_source_maps(assets)
