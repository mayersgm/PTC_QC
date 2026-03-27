#!/usr/bin/env python3
"""Extract embedded images and hyperlink list from PTC_QC_Procedures_v1.1.pdf (PyMuPDF)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "PTC_QC_Procedures_v1.1.pdf"
OUT = ROOT / "assets" / "pdf_v1.1"


def main() -> None:
    try:
        import fitz
    except ImportError:
        sys.path.insert(0, str(ROOT / ".pdf_tools"))
        import fitz  # type: ignore

    if not PDF.exists():
        raise FileNotFoundError(f"Missing {PDF}")

    OUT.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF)
    links: list[dict] = []
    seen: set[tuple[int, str]] = set()
    for page in doc:
        for link in page.get_links():
            uri = link.get("uri")
            if not uri:
                continue
            key = (page.number + 1, uri)
            if key in seen:
                continue
            seen.add(key)
            links.append({"page": page.number + 1, "uri": uri})

    img_count = 0
    for i, page in enumerate(doc):
        for img in page.get_images(full=True):
            xref = img[0]
            data = doc.extract_image(xref)
            if not data:
                continue
            img_count += 1
            ext = data.get("ext", "png")
            name = f"page{i + 1:02d}_img{img_count:03d}.{ext}"
            (OUT / name).write_bytes(data["image"])

    (OUT / "extracted_links.json").write_text(json.dumps(links, indent=2), encoding="utf-8")
    print(f"Wrote {img_count} images and {len(links)} link rows to {OUT}")


if __name__ == "__main__":
    main()
