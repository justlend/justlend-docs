# JustLend DAO Documentation
This is the official developer documentation for the JustLend DAO, providing comprehensive development guides and API references.

## 🚀 Community
- [JUST-Defi](https://t.me/just_defi)
- [JustLend DAO Official](https://t.me/officialjustlend)

## 🔧 Tech Stack

- [MkDocs](https://www.mkdocs.org/) - Static site generator
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) - Theme
- [GitHub Pages](https://pages.github.com/) - Hosting service
- [GitHub Actions](https://github.com/features/actions) - CI/CD for deployment

## 🛠️ Local Development

Recommended Node.js version for the verification scripts: **24.22.1**, pinned in `.nvmrc` and CI.
With nvm installed, run `nvm install && nvm use` before the Node.js checks below.
MkDocs uses Python 3.12 and the hashed dependency locks below. `requirements.txt`
and `requirements-test.txt` are inputs; CI and local builds install the locks.

```bash
python -m pip install --require-hashes -r requirements.lock
mkdocs serve
```

Before opening a pull request, run:

```bash
mkdocs build --strict
```

For the documentation verification regressions (offline; no wallet signing or broadcasts):

```bash
python -m pip install --require-hashes -r requirements-test.lock
python -m pip check
python -m unittest scripts.test_dependency_security
node scripts/verify-ai-consistency.mjs
node scripts/normalize-mcp-catalog.mjs --check
node --test scripts/api-acceptance.test.mjs
python scripts/test-docs-regressions.py
mkdocs build --strict
DOCS_SITE_DIR=site python scripts/test-docs-regressions.py
python hooks/secure_swagger.py --site-dir site
DOCS_SITE_DIR=site python -m unittest scripts.test_dependency_security.BuiltSite
```

### Dependency and browser-asset updates

Regenerate build and test locks together with uv 0.11.2 (or a reviewed newer
version), then test a fresh environment. The static legacy-package metadata in
`pyproject.toml` covers reviewed jieba 0.42.1 and mkdocs-exclude 1.0.2 source distributions, avoiding
setup.py execution during resolution. Installation still builds these legacy
source packages after verifying their hashes; re-review setup.py if upgrading them.

```bash
uv pip compile --python-version 3.12 --generate-hashes requirements.txt -o requirements.lock
uv pip compile --python-version 3.12 --generate-hashes -c requirements.lock requirements-test.txt -o requirements-test.lock
pip-audit --no-deps --disable-pip -r requirements.lock
pip-audit --no-deps --disable-pip -r requirements-test.lock
python hooks/secure_swagger.py --site-dir site --audit
```

The pinned Swagger plugin still ships older frontend files. The late
`hooks/secure_swagger.py` hook replaces **all** published Swagger JS, CSS, source
maps, license notices and OAuth redirect files with the same-release artifacts
under `vendor/swagger-ui/`. It checks SHA-256 values before copying and in the
generated site; it never downloads an unpinned CDN bundle or silently falls back.
`vendor/swagger-ui/manifest.json` records the npm tarball URL/integrity and the
embedded DOMPurify version. To update, verify a reviewed `swagger-ui-dist`
tarball against its npm integrity, replace the complete mapped asset set plus
LICENSE/NOTICE, regenerate the manifest, and run offline tests, strict build and
the OSV audit. A clean Python audit alone does not cover bundled JavaScript.

Custom page additions live in `docs/overrides/main.html`, extending the installed
theme's base instead of copying its hashed JS/CSS/search-worker references.

Product-facing interface sources, targets, verification dates and coverage belong in `docs/developers/abis/manifest.json` and the related reference pages. Offline observations used by regressions are in `scripts/fixtures/docs-verification/abi-provenance-20261014.json`, outside the published `docs/` tree. Issue checklists, acceptance status and full collection archives belong in the PR or local review report, not site navigation or search.

After importing the generated MCP catalog, run `node scripts/normalize-mcp-catalog.mjs`
to apply the docs-local table escaping and transaction/configuration distinctions.


## 🤝 Contact Us

- Official Website: [Documentation Website](https://docs.justlend.org/)
- JustLend Website: [App Website](https://justlend.org)

## 📚 Related Links

- [JustLend Official Site](https://www.justlend.org/)
- [Just Official Site](https://just.network/)
