"""Offline dependency/artifact regressions; never exercise a live API."""
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def load_hook():
    spec = importlib.util.spec_from_file_location("secure_swagger", ROOT / "hooks/secure_swagger.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourcePolicy(unittest.TestCase):
    def test_fixed_python_versions_are_explicit(self):
        text = (ROOT / "requirements.txt").read_text()
        for pin in ("mkdocs-material==9.7.7", "pymdown-extensions==11.0.1", "pygments==2.20.0"):
            self.assertIn(pin, text)

    def test_theme_inherits_upstream_assets_and_preserves_discovery(self):
        self.assertFalse((ROOT / "docs/overrides/base.html").exists())
        text = (ROOT / "docs/overrides/main.html").read_text()
        self.assertIn('{% extends "base.html" %}', text)
        for marker in ('rel="llms"', 'type="application/ld+json"', 'type="text/markdown"'):
            self.assertIn(marker, text)
        self.assertNotIn("bundle.c8b220af", text)
        self.assertIn('{% extends "main.html" %}', (ROOT / "docs/overrides/404.html").read_text())

    def test_ci_installs_and_audits_locked_dependencies(self):
        workflow = (ROOT / ".github/workflows/gh-pages.yml").read_text()
        self.assertIn("--require-hashes -r requirements-test.lock", workflow)
        self.assertNotIn("pip install pygments", workflow)
        self.assertIn("python-version: '3.12'", workflow)
        self.assertIn("--disable-pip", workflow)
        self.assertIn("hooks/secure_swagger.py --site-dir site", workflow)
        for name in ("requirements.lock", "requirements-test.lock"):
            text = (ROOT / name).read_text()
            self.assertIn("--hash=sha256:", text)
            self.assertIn("jieba==0.42.1", text)


class AssetSafety(unittest.TestCase):
    def setUp(self):
        self.hook = load_hook()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        (self.root / "vendor").mkdir(parents=True)
        shutil.copytree(ROOT / "vendor/swagger-ui", self.root / "vendor/swagger-ui")
        self.site = Path(self.temporary.name) / "site"
        self.site.mkdir()

    def test_patched_sources_and_output_match_official_artifacts(self):
        manifest = self.hook.verify_sources(self.root)
        self.assertEqual(manifest["packages"], {"swagger-ui-dist": "5.34.1", "dompurify": "3.4.17"})
        self.hook.copy_assets(self.root, self.site)
        self.hook.verify_site(self.root, self.site)
        for source, target in self.hook.ASSETS.items():
            self.assertEqual((self.root / "vendor/swagger-ui" / source).read_bytes(), (self.site / target).read_bytes())

    def test_corrupt_source_fails_before_any_copy(self):
        source = self.root / "vendor/swagger-ui/swagger-ui-bundle.js"
        source.write_bytes(source.read_bytes() + b"corruption")
        with self.assertRaisesRegex(ValueError, "hash"):
            self.hook.copy_assets(self.root, self.site)
        self.assertEqual(list(self.site.iterdir()), [])

    def test_missing_source_is_not_replaced_with_old_plugin_asset(self):
        (self.root / "vendor/swagger-ui/swagger-ui-bundle.js").unlink()
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.hook.copy_assets(self.root, self.site)

    def test_output_symlink_cannot_escape_site_directory(self):
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (self.site / "assets").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "outside"):
            self.hook.copy_assets(self.root, self.site)
        self.assertEqual(list(outside.iterdir()), [])

    def test_built_bundle_tampering_is_detected(self):
        self.hook.copy_assets(self.root, self.site)
        target = self.site / "assets/javascripts/swagger-ui-bundle.js"
        target.write_bytes(target.read_bytes() + b"corruption")
        with self.assertRaisesRegex(ValueError, "hash"):
            self.hook.verify_site(self.root, self.site)

    def test_hook_runs_after_default_plugin_copy(self):
        self.assertLess(self.hook.on_post_build.mkdocs_priority, 0)
        self.assertIn("hooks/secure_swagger.py", (ROOT / "mkdocs.yml").read_text())


class AdvisoryService(unittest.TestCase):
    def test_empty_advisory_response_is_clean(self):
        reply = Mock()
        reply.json.return_value = {}
        with patch("requests.post", return_value=reply):
            rows = load_hook().audit_packages({"packages": {"dompurify": "3.4.17"}})
        self.assertEqual(rows[0]["advisories"], [])

    def test_known_advisory_is_not_hidden(self):
        reply = Mock()
        reply.json.return_value = {"vulns": [{"id": "GHSA-offline-fixture"}]}
        with patch("requests.post", return_value=reply):
            rows = load_hook().audit_packages({"packages": {"dompurify": "3.4.17"}})
        self.assertEqual(rows[0]["advisories"], ["GHSA-offline-fixture"])

    def test_error_payload_is_not_a_clean_result(self):
        reply = Mock()
        reply.json.return_value = {"error": "service unavailable"}
        with patch("requests.post", return_value=reply):
            with self.assertRaisesRegex(ValueError, "OSV response"):
                load_hook().audit_packages({"packages": {"dompurify": "3.4.17"}})


class PageAssets(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.references = []
        self.jsonld = []
        self.configs = []
        self.raw_markdown = False
        self.footer_count = 0
        self.capture = None
        self.buffer = ""
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.references.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.references.append(attrs["href"])
        if attrs.get("type") == "text/markdown":
            self.raw_markdown = True
        if "content-footer-divider" in attrs.get("class", "").split():
            self.footer_count += 1
        if tag == "script":
            self.buffer = ""
            self.capture = ("jsonld" if attrs.get("type") == "application/ld+json" else
                            "config" if attrs.get("id") == "__config" else None)

    def handle_data(self, data):
        if self.capture:
            self.buffer += data

    def handle_endtag(self, tag):
        if tag == "script" and self.capture:
            parsed = json.loads(self.buffer)
            (self.jsonld if self.capture == "jsonld" else self.configs).append(parsed)
            self.capture = None


@unittest.skipUnless(os.environ.get("DOCS_SITE_DIR"), "requires generated site")
class BuiltSite(unittest.TestCase):
    def setUp(self):
        self.site = Path(os.environ["DOCS_SITE_DIR"]).resolve()

    def check_reference(self, page, reference):
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            return
        path = unquote(url.path)
        target = self.site / path.lstrip("/") if path.startswith("/") else page.parent / path
        self.assertTrue(target.resolve().is_relative_to(self.site), reference)
        self.assertTrue(target.is_file(), f"{page.relative_to(self.site)}: missing {reference}")

    def test_every_local_script_stylesheet_and_search_worker_exists(self):
        self.assertFalse((self.site / "overrides").exists(), "raw Jinja templates must not be published")
        for page in self.site.rglob("*.html"):
            parsed = PageAssets(page.read_text())
            for reference in parsed.references:
                self.check_reference(page, reference)
            for config in parsed.configs:
                if config.get("search"):
                    self.check_reference(page, config["search"])

    def test_discovery_metadata_and_footer_survive_inheritance(self):
        for path in ["getting_started/overview/index.html", "developers/apis/index.html"]:
            page = self.site / path
            text = page.read_text()
            parsed = PageAssets(text)
            self.assertEqual(len(parsed.jsonld), 1, path)
            self.assertIn('rel="llms"', text)
            self.assertTrue(parsed.raw_markdown, path)
            self.assertEqual(parsed.footer_count, 1, path)
        self.assertEqual(len(PageAssets((self.site / "404.html").read_text()).jsonld), 1)


if __name__ == "__main__":
    unittest.main()
