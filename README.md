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

```bash
python -m pip install -r requirements.txt
mkdocs serve
```

Before opening a pull request, run:

```bash
node --test scripts/api-acceptance.test.mjs
mkdocs build --strict
```

## CI and live API monitoring

- **Publish Document** runs source consistency checks, offline API CLI regression tests,
  and the strict documentation build. Failed checks still block deployment; pull requests
  never deploy. Live API availability is not a documentation deployment prerequisite.
- **Monitor Live API** runs the nine read-only production probes every Monday at 02:17 UTC
  or manually through GitHub Actions. Failed probes fail this independent workflow and
  print diagnostics to stderr; the JSON report is retained as a run artifact for 14 days,
  including on failure. This workflow never deploys or updates repository files.
- The published `agent-acceptance-latest.json` is the committed verification snapshot,
  not a live status feed. Check its `generatedAt` timestamp. Refresh it only after a
  successful, reviewed live run; current monitoring results are in the monitor's run artifacts.

## 🤝 Contact Us

- Official Website: [Documentation Website](https://docs.justlend.org/)
- JustLend Website: [App Website](https://justlend.org)

## 📚 Related Links

- [JustLend Official Site](https://www.justlend.org/)
- [Just Official Site](https://just.network/)
