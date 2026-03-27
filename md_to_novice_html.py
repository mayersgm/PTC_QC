#!/usr/bin/env python3
from __future__ import annotations

import re
import html as html_lib
from datetime import datetime
from pathlib import Path

from markdown_it import MarkdownIt


SRC = Path("PTC_QC_Procedures_v1.1_novice.md")
DST = Path("PTC_QC_Procedures_v1.1_novice.html")


def add_copy_buttons(rendered_html: str) -> str:
    pattern = re.compile(r"<pre><code(?: class=\"language-([^\"]+)\")?>(.*?)</code></pre>", re.DOTALL)

    def repl(match: re.Match) -> str:
        lang = (match.group(1) or "").lower()
        code_html = match.group(2)
        is_cmd = lang in {"bash", "sh", "shell"}
        css_class = "cmd-block" if is_cmd else "code-block"
        code_class_attr = f' class="language-{lang}"' if lang else ""
        if is_cmd:
            lines = code_html.split("\n")
            cmd_rows = []
            for raw in lines:
                stripped = raw.strip()
                if not stripped:
                    continue
                decoded = html_lib.unescape(stripped)
                if decoded.startswith("#"):
                    cmd_rows.append(f'<div class="cmd-note">{stripped}</div>')
                    continue
                escaped_data = html_lib.escape(decoded, quote=True)
                cmd_rows.append(
                    '<div class="cmd-line">'
                    f'<code class="cmd-text">{stripped}</code>'
                    f'<button class="copy-line-btn" type="button" data-cmd="{escaped_data}">Copy</button>'
                    "</div>"
                )
            rows_html = "".join(cmd_rows)
            return (
                f'<div class="{css_class}">'
                '<div class="cmd-toolbar">'
                '<span class="cmd-toolbar-title">Command sequence</span>'
                '<button class="copy-btn copy-block-btn" type="button">Copy block</button>'
                "</div>"
                f"<pre><code{code_class_attr}>{code_html}</code></pre>"
                f'<div class="cmd-lines">{rows_html}</div>'
                "</div>"
            )
        return (
            f'<div class="{css_class}">'
            f'<button class="copy-btn" type="button">Copy</button>'
            f"<pre><code{code_class_attr}>{code_html}</code></pre>"
            "</div>"
        )

    return pattern.sub(repl, rendered_html)


def wrap_html(body: str) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PTC QC Procedure - Beginner-Friendly</title>
  <style>
    :root {{
      --bg: #f7f8fb;
      --paper: #ffffff;
      --ink: #1f2937;
      --muted: #6b7280;
      --line: #d1d5db;
      --cmd-bg: #0f172a;
      --cmd-ink: #e2e8f0;
      --btn: #2563eb;
      --btn-hover: #1d4ed8;
      --good: #065f46;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.55;
    }}
    .page {{
      max-width: 980px;
      margin: 20px auto 40px;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 10px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.06);
      padding: 32px 40px;
    }}
    .meta {{
      color: var(--muted);
      font-size: 0.92rem;
      margin-bottom: 18px;
    }}
    h1, h2, h3 {{ line-height: 1.25; }}
    h1 {{ margin-top: 0; font-size: 2rem; }}
    h2 {{
      margin-top: 28px;
      padding-top: 10px;
      border-top: 1px solid #e5e7eb;
      font-size: 1.35rem;
    }}
    h3 {{ margin-top: 20px; font-size: 1.1rem; }}
    p code, li code {{
      background: #eef2ff;
      border: 1px solid #c7d2fe;
      padding: 2px 5px;
      border-radius: 4px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.94em;
    }}
    .copy-tip {{
      padding: 10px 12px;
      border: 1px solid #bfdbfe;
      background: #eff6ff;
      color: #1e3a8a;
      border-radius: 8px;
      margin: 12px 0 20px;
      font-size: 0.95rem;
    }}
    .cmd-block, .code-block {{
      position: relative;
      margin: 14px 0 18px;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid #1f2937;
    }}
    .cmd-block pre, .code-block pre {{
      margin: 0;
      padding: 14px;
      overflow-x: auto;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.9rem;
      white-space: pre;
    }}
    .cmd-block pre {{
      background: var(--cmd-bg);
      color: var(--cmd-ink);
    }}
    .code-block pre {{
      background: #111827;
      color: #d1d5db;
    }}
    .copy-btn {{
      position: absolute;
      top: 8px;
      right: 8px;
      background: var(--btn);
      color: #fff;
      border: none;
      border-radius: 6px;
      padding: 6px 10px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
    }}
    .copy-btn:hover {{ background: var(--btn-hover); }}
    .copy-btn.copied {{
      background: var(--good);
    }}
    .cmd-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 10px;
      background: #0b1220;
      border-bottom: 1px solid #1f2937;
    }}
    .cmd-toolbar-title {{
      color: #9ca3af;
      font-size: 0.82rem;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    .copy-block-btn {{
      position: static;
      padding: 4px 9px;
      font-size: 0.75rem;
    }}
    .cmd-lines {{
      background: #f9fafb;
      border-top: 1px solid #d1d5db;
      padding: 8px;
    }}
    .cmd-line {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      padding: 6px 8px;
      margin-bottom: 7px;
      background: #ffffff;
    }}
    .cmd-line:last-child {{ margin-bottom: 0; }}
    .cmd-text {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.85rem;
      color: #0f172a;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .copy-line-btn {{
      border: none;
      border-radius: 6px;
      background: #1d4ed8;
      color: #fff;
      padding: 5px 9px;
      font-size: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      flex-shrink: 0;
    }}
    .copy-line-btn:hover {{ background: #1e40af; }}
    .copy-line-btn.copied {{ background: var(--good); }}
    .cmd-note {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.78rem;
      color: #6b7280;
      margin: 2px 0 8px;
      padding: 2px 4px;
    }}
    hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }}
    @media print {{
      body {{ background: #fff; }}
      .page {{
        box-shadow: none;
        border: none;
        margin: 0;
        max-width: none;
        padding: 0;
      }}
      .copy-btn {{ display: none; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <div class="meta">Generated from novice markdown on {generated}</div>
    <div class="copy-tip"><strong>Tip:</strong> Click <strong>Copy</strong> on any command block, then paste into Terminal.</div>
    {body}
  </main>
  <script>
    document.querySelectorAll('.copy-btn').forEach((btn) => {{
      btn.addEventListener('click', async () => {{
        const codeEl = btn.parentElement.querySelector('code');
        const text = codeEl ? codeEl.textContent : '';
        try {{
          await navigator.clipboard.writeText(text);
          const old = btn.textContent;
          btn.textContent = 'Copied';
          btn.classList.add('copied');
          setTimeout(() => {{
            btn.textContent = old;
            btn.classList.remove('copied');
          }}, 1200);
        }} catch (_err) {{
          btn.textContent = 'Copy failed';
          setTimeout(() => btn.textContent = 'Copy', 1200);
        }}
      }});
    }});
    document.querySelectorAll('.copy-line-btn').forEach((btn) => {{
      btn.addEventListener('click', async () => {{
        const text = btn.getAttribute('data-cmd') || '';
        try {{
          await navigator.clipboard.writeText(text);
          const old = btn.textContent;
          btn.textContent = 'Copied';
          btn.classList.add('copied');
          setTimeout(() => {{
            btn.textContent = old;
            btn.classList.remove('copied');
          }}, 1200);
        }} catch (_err) {{
          btn.textContent = 'Copy failed';
          setTimeout(() => btn.textContent = 'Copy', 1200);
        }}
      }});
    }});
  </script>
</body>
</html>
"""


def main():
    if not SRC.exists():
        raise FileNotFoundError(f"Input markdown not found: {SRC}")

    md = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})
    text = SRC.read_text(encoding="utf-8")
    rendered = md.render(text)
    rendered = add_copy_buttons(rendered)
    html = wrap_html(rendered)
    DST.write_text(html, encoding="utf-8")
    print(f"Created: {DST.resolve()}")


if __name__ == "__main__":
    main()
