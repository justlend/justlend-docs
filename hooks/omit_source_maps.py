"""Keep vendor debug maps out of the published site without removing the runtime assets."""

from pathlib import Path

from mkdocs.plugins import event_priority


@event_priority(-100)  # Swagger UI copies its assets in its own on_post_build hook.
def on_post_build(*, config) -> None:
    for source_map in (Path(config.site_dir) / "assets").rglob("*.map"):
        bundle = source_map.with_suffix("")
        if bundle.suffix not in {".js", ".css"} or not source_map.is_file():
            continue

        if bundle.is_file():
            # Remove only the terminal DevTools comment for this exact sibling.
            name = source_map.name.encode()
            trailer = (
                b"//# sourceMappingURL=" + name
                if bundle.suffix == ".js"
                else b"/*# sourceMappingURL=" + name + b"*/"
            )
            content = bundle.read_bytes().rstrip(b"\r\n")
            if content.endswith(trailer):
                bundle.write_bytes(content[:-len(trailer)])
        source_map.unlink()
