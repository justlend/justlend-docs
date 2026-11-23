"""Publication policy: remove debug sidecars and only their terminal local directives."""

import re


def without_source_map(content: bytes, filename: str) -> bytes:
    """Return the vendor bytes unchanged except for a terminal reference to this asset's map."""
    reference = rb"sourceMappingURL[ \t]*=[ \t]*(?:\./)?" + re.escape((filename + ".map").encode())
    if filename.endswith(".js"):
        trailer = rb"//#[ \t]*" + reference
    elif filename.endswith(".css"):
        trailer = rb"/\*#[ \t]*" + reference + rb"[ \t]*\*/"
    else:
        return content
    return re.sub(trailer + rb"[ \t\r\n]*\Z", b"", content)


def omit_source_maps(assets):
    for path in assets.rglob("*"):
        if not path.is_file():
            continue
        if path.name.endswith((".js.map", ".css.map")):
            path.unlink()
        elif path.suffix in {".js", ".css"}:
            original = path.read_bytes()
            published = without_source_map(original, path.name)
            if published != original:
                path.write_bytes(published)
