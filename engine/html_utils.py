from html import escape
from pathlib import Path
from typing import Iterable

from engine.io_utils import write_text


def markdown_to_html_page(title: str, markdown: str) -> str:
    body = _markdown_to_body(markdown)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="zh-CN">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(title)}</title>",
            "<style>",
            "body{font-family:Arial,sans-serif;line-height:1.6;max-width:1080px;margin:32px auto;padding:0 20px;color:#1f2937;}",
            "article{padding:24px;border:1px solid #e5e7eb;border-radius:8px;}",
            "h1,h2,h3{line-height:1.2;}",
            "table{width:100%;border-collapse:collapse;margin:16px 0;}",
            "th,td{border:1px solid #e5e7eb;padding:8px;vertical-align:top;text-align:left;}",
            "ul{margin:8px 0 16px 24px;}",
            "p{margin:8px 0;}",
            "pre{background:#f3f4f6;padding:12px;border-radius:6px;overflow:auto;}",
            "code{font-family:Consolas,monospace;}",
            "</style>",
            "</head>",
            "<body>",
            "<article>",
            f"<h1>{escape(title)}</h1>",
            body,
            "</article>",
            "</body>",
            "</html>",
            "",
        ]
    )


def write_markdown_html_sidecar(path: Path, title: str, markdown: str) -> Path:
    html_path = path.with_suffix(".html")
    write_text(html_path, markdown_to_html_page(title, markdown))
    return html_path


def _markdown_to_body(markdown: str) -> str:
    lines = markdown.splitlines()
    html_parts: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            fence, i = _consume_code_block(lines, i + 1)
            html_parts.append(f"<pre><code>{escape(fence)}</code></pre>")
            continue
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            level = max(1, min(level, 3))
            html_parts.append(f"<h{level}>{escape(text)}</h{level}>")
            i += 1
            continue
        if _is_table_row(stripped):
            table_html, i = _consume_table(lines, i)
            html_parts.append(table_html)
            continue
        if _is_list_item(stripped):
            list_html, i = _consume_list(lines, i)
            html_parts.append(list_html)
            continue

        paragraph, i = _consume_paragraph(lines, i)
        html_parts.append(f"<p>{escape(paragraph)}</p>")
    return "\n".join(html_parts)


def _consume_code_block(lines: list[str], start_index: int) -> tuple[str, int]:
    code_lines: list[str] = []
    i = start_index
    while i < len(lines) and not lines[i].strip().startswith("```"):
        code_lines.append(lines[i])
        i += 1
    if i < len(lines):
        i += 1
    return "\n".join(code_lines), i


def _consume_table(lines: list[str], start_index: int) -> tuple[str, int]:
    rows: list[list[str]] = []
    i = start_index
    while i < len(lines) and _is_table_row(lines[i].strip()):
        rows.append(_split_table_row(lines[i].strip()))
        i += 1
    if len(rows) >= 2 and all(_is_separator_cell(cell) for cell in rows[1]):
        header = rows[0]
        body_rows = rows[2:]
    else:
        header = rows[0]
        body_rows = rows[1:]
    html_rows = ["<table><thead><tr>"]
    html_rows.extend(f"<th>{escape(cell)}</th>" for cell in header)
    html_rows.append("</tr></thead><tbody>")
    for row in body_rows:
        html_rows.append("<tr>")
        html_rows.extend(f"<td>{escape(cell)}</td>" for cell in row)
        html_rows.append("</tr>")
    html_rows.append("</tbody></table>")
    return "".join(html_rows), i


def _consume_list(lines: list[str], start_index: int) -> tuple[str, int]:
    items: list[str] = []
    i = start_index
    while i < len(lines):
        stripped = lines[i].strip()
        if not _is_list_item(stripped):
            break
        items.append(escape(stripped[2:].strip()))
        i += 1
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>", i


def _consume_paragraph(lines: list[str], start_index: int) -> tuple[str, int]:
    parts: list[str] = []
    i = start_index
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("#") or _is_list_item(stripped) or _is_table_row(stripped) or stripped.startswith("```"):
            break
        parts.append(stripped)
        i += 1
    return " ".join(parts), i


def _is_list_item(line: str) -> bool:
    return line.startswith("- ") or line.startswith("* ")


def _is_table_row(line: str) -> bool:
    return line.startswith("|") and line.endswith("|")


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip("|").split("|")]


def _is_separator_cell(cell: str) -> bool:
    stripped = cell.replace(" ", "")
    return stripped != "" and set(stripped) <= {"-"}
