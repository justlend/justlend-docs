"""Offline regression tests for what can ship and what the separate advisory scan gates."""

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("swagger_check", Path(__file__).with_name("verify-swagger-ui.py"))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class PublishedAssets(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.site = Path(temp.name) / "site"
        self.dist = Path(temp.name) / "dist"
        self.assets = self.site / "assets"
        self.page = self.site / "developers/apis/index.html"
        self.page.parent.mkdir(parents=True)
        self.assets.mkdir()
        self.dist.mkdir()
        self.enterContext(patch.object(check, "DIST", self.dist))
        self.page.write_text('<iframe class="swagger-ui-iframe" src="/frame.html"></iframe>')
        self.names = ["swagger-ui-bundle.js", "swagger-ui-standalone-preset.js"]
        (self.site / "frame.html").write_text("".join(f'<script src="/assets/{n}"></script>' for n in self.names))
        for name in self.names:
            (self.dist / name).write_bytes(b'run();\n')
            (self.assets / name).write_bytes(b'run();\n')

    def test_cleanup_handles_sidecars_and_trailers_independently(self):
        from omit_source_maps import omit_source_maps

        stray = self.assets / "old.js.map"
        stray.touch()  # Left by the iframe plugin, even if its JS was replaced.
        for name, trailer in [
            ("a.js", b"//# sourceMappingURL=a.js.map\r\n"),
            ("b.css", b"/*# sourceMappingURL=b.css.map*/"),
            ("c.css", b"/*# sourceMappingURL=c.css.map */\n"),
            ("d.css", b"/*# sourceMappingURL=d.css.map  */\r\n"),
        ]:
            (self.assets / name).write_bytes(b"work();\r\n" + trailer)
        (self.assets / "a.js.map").touch()  # Other trailers have no sibling map.
        untouched = {
            "plain.js": b"run();\n\n", "data.map": b"unrelated",
            "else.js": b"//# sourceMappingURL=other.js.map\n",
            "middle.css": b"/*# sourceMappingURL=middle.css.map */\n.a{}",
        }
        for name, data in untouched.items():
            (self.assets / name).write_bytes(data)
        omit_source_maps(self.assets)
        for name in ("a.js", "b.css", "c.css", "d.css"):
            self.assertEqual((self.assets / name).read_bytes(), b"work();\r\n")
        for name, data in untouched.items():
            self.assertEqual((self.assets / name).read_bytes(), data)
        self.assertFalse(stray.exists())
        self.assertFalse((self.assets / "a.js.map").exists())

    def test_offline_check_accepts_only_the_locked_runtime_bytes(self):
        with patch("socket.socket.connect", side_effect=AssertionError("verification must be offline")):
            check.verify(self.site, "test")
            name = self.names[0]
            (self.dist / name).write_bytes(b"run();\n//# sourceMappingURL=swagger-ui-bundle.js.map\n")
            check.verify(self.site, "test")
            for bad in (b"edited();\n", (self.dist / name).read_bytes()):
                with self.subTest(bad=bad), self.assertRaises(SystemExit):
                    (self.assets / name).write_bytes(bad)
                    check.verify(self.site, "test")

    def test_remote_missing_or_duplicate_script_is_not_a_valid_page(self):
        for src in ("https://example.org/x.js", "missing.js", "/assets/" + self.names[1]):
            with self.subTest(src=src), self.assertRaises(SystemExit):
                frame = self.site / "frame.html"
                frame.write_text(f'<script src="{src}"></script><script src="/assets/{self.names[1]}"></script>')
                check.verify(self.site, "test")

    def test_audit_uses_browser_inventory_and_severity(self):
        (self.dist / self.names[0]).write_bytes(b'PACKAGE_VERSION:"1.0",GIT_COMMIT:"abc1234"')
        (self.dist / "log.bundle-sizes.swagger-ui.txt").write_text("immutable: 1 KB\njs-yaml: 1 KB\n<self>: 1 KB\n")
        lock = {"packages": {
            "node_modules/immutable": {"version": "1", "dev": True},
            "node_modules/js-yaml": {"version": "2"},
            "node_modules/upstream-only": {"version": "3"},
        }}
        for severity in ("moderate", "high", "critical"):
            def registry(url, payload=None):
                if payload is None:
                    return lock
                self.assertEqual(payload, {"immutable": ["1"], "js-yaml": ["2"], "swagger-ui-dist": ["1.0"]})
                # Even an unexpected record for a package not in the request must not gate the bundle.
                return {name: [{"severity": level, "url": "https://example.org/advisory"}]
                        for name, level in [("upstream-only", "critical"), ("immutable", severity)]}
            with (
                self.subTest(severity=severity),
                patch.object(check, "fetch_json", side_effect=registry),
                redirect_stdout(io.StringIO()) as output,
            ):
                if severity == "moderate":
                    check.audit("1.0")
                else:
                    with self.assertRaises(SystemExit):
                        check.audit("1.0")
                self.assertIn(f"{severity} immutable", output.getvalue())
        with patch.object(check, "fetch_json", return_value={"packages": {}}), self.assertRaises(SystemExit):
            check.audit("1.0")
        with patch.object(check, "fetch_json", side_effect=OSError("unavailable")), self.assertRaises(OSError):
            check.audit("1.0")


if __name__ == "__main__":
    unittest.main()
