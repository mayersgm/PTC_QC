#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


SRC = Path("PTC_QC_Procedures_v1.1_novice.md")
DST = Path("PTC_QC_Procedures_v1.1_novice.pdf")


def build_styles():
    base = getSampleStyleSheet()
    styles = {
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=11,
            leading=15,
            spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=18,
            leading=22,
            spaceBefore=14,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Times-BoldItalic",
            fontSize=12,
            leading=15,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=9,
            leading=12,
            leftIndent=16,
            backColor=colors.HexColor("#F5F5F5"),
            borderColor=colors.HexColor("#D8D8D8"),
            borderWidth=0.5,
            borderPadding=6,
            borderRadius=2,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "toc_header": ParagraphStyle(
            "TOCHeader",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=15,
            leading=19,
            spaceAfter=8,
        ),
    }
    return styles


class ProcedureDocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._headings = []

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and hasattr(flowable, "_toc_level"):
            text = flowable.getPlainText()
            level = getattr(flowable, "_toc_level", 0)
            key = f"h{len(self._headings)}"
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (level, text, self.page, key))
            self._headings.append((level, text, self.page))


def parse_markdown(lines, styles):
    story = []
    bullets = []
    code_mode = False
    code_buf = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            items = [ListItem(Paragraph(item, styles["body"])) for item in bullets]
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    leftIndent=18,
                    bulletFontName="Times-Roman",
                    bulletFontSize=10,
                )
            )
            story.append(Spacer(1, 4))
            bullets = []

    def flush_code():
        nonlocal code_buf
        if code_buf:
            story.append(Preformatted("\n".join(code_buf), styles["code"]))
            code_buf = []

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            if code_mode:
                flush_code()
                code_mode = False
            else:
                flush_bullets()
                code_mode = True
            continue

        if code_mode:
            code_buf.append(line)
            continue

        if stripped == "---":
            flush_bullets()
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#777777")))
            story.append(Spacer(1, 8))
            continue

        h1 = re.match(r"^#\s+(.+)", stripped)
        h2 = re.match(r"^##\s+(.+)", stripped)
        h3 = re.match(r"^###\s+(.+)", stripped)
        if h1 or h2 or h3:
            flush_bullets()
            txt = (h1 or h2 or h3).group(1).strip()
            if h1:
                p = Paragraph(txt, styles["h1"])
                p._toc_level = 0
            elif h2:
                p = Paragraph(txt, styles["h2"])
                p._toc_level = 1
            else:
                p = Paragraph(txt, styles["h3"])
                p._toc_level = 2
            story.append(p)
            continue

        if re.match(r"^-\s+.+", stripped):
            bullets.append(re.sub(r"^-\s+", "", stripped))
            continue

        if re.match(r"^\d+\.\s+.+", stripped):
            flush_bullets()
            story.append(Paragraph(stripped, styles["body"]))
            continue

        if not stripped:
            flush_bullets()
            story.append(Spacer(1, 4))
            continue

        flush_bullets()
        body_text = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        body_text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", body_text)
        story.append(Paragraph(body_text, styles["body"]))

    flush_bullets()
    flush_code()
    return story


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(doc.leftMargin, 0.55 * inch, "PTC Quality Control Procedure - Beginner-Friendly")
    canvas.drawRightString(LETTER[0] - doc.rightMargin, 0.55 * inch, f"Page {doc.page}")
    canvas.restoreState()


def main():
    if not SRC.exists():
        raise FileNotFoundError(f"Source markdown not found: {SRC}")

    styles = build_styles()
    md_lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)

    doc = ProcedureDocTemplate(
        str(DST),
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title="PTC QC Procedures (Novice)",
        author="UPenn Electronics QC Team",
    )

    story = []

    # Cover page
    cover_table = Table(
        [
            [Paragraph("PTC Quality Control Test Setup", styles["h1"])],
            [Paragraph("&amp; Quality Control Procedure", styles["h2"])],
            [Paragraph("Beginner-Friendly Edition", styles["h3"])],
            [Paragraph("Version v1.1 novice rewrite", styles["body"])],
            [Paragraph(f"Generated {datetime.now().strftime('%Y-%m-%d')}", styles["body"])],
        ],
        colWidths=[6.8 * inch],
    )
    cover_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#333333")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#AAAAAA")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F1F1")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    story.append(Spacer(1, 1.8 * inch))
    story.append(cover_table)
    story.append(Spacer(1, 0.6 * inch))
    story.append(
        Paragraph(
            "This document is intended for first-time operators with no assumed Linux command-line experience.",
            styles["body"],
        )
    )
    story.append(PageBreak())

    # TOC page
    story.append(Paragraph("Contents", styles["toc_header"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(fontName="Times-Roman", fontSize=11, name="TOCLevel1", leftIndent=20, firstLineIndent=-10, spaceBefore=5),
        ParagraphStyle(fontName="Times-Roman", fontSize=10, name="TOCLevel2", leftIndent=40, firstLineIndent=-10, spaceBefore=2),
        ParagraphStyle(fontName="Times-Italic", fontSize=10, name="TOCLevel3", leftIndent=60, firstLineIndent=-10, spaceBefore=1),
    ]
    story.append(toc)
    story.append(PageBreak())

    story.extend(parse_markdown(md_lines, styles))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"Created: {DST.resolve()}")


if __name__ == "__main__":
    main()
