from pathlib import Path

from engine.io_utils import read_text, write_text
from engine.paths import books_dir, knowledge_dir

BOOKS_DIR = books_dir()
KNOWLEDGE_DIR = knowledge_dir()

YAML_FILES = [
    ("Story Bible", "canon/novel_bible.yaml"),
    ("Characters", "canon/characters.yaml"),
    ("Character States", "canon/character_states.yaml"),
    ("Timeline", "canon/timeline.yaml"),
    ("Open Threads", "canon/open_threads.yaml"),
    ("Resource Ledger", "canon/resource_ledger.yaml"),
    ("Payoff Ledger", "canon/payoff_ledger.yaml"),
    ("Relevant Outline", "outlines/arc_001.yaml"),
    # V3 ledgers are still small; later versions can slice by relevance.
    ("Unit Plan", "outlines/units/unit_0001.yaml"),
]

JSON_FILES = [
    ("Current State", "state/current_state.json"),
    ("Chapter Index", "state/chapter_index.json"),
    ("Hook Index", "state/hook_index.json"),
    ("Memory Index", "state/memory_index.json"),
]


def build_context(book_id: str, chapter_number: int) -> str:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    title = _read_title(root)
    sections = [
        f"# Chapter {chapter_number:04d} Context Pack",
        "",
        "## Book Metadata",
        "",
        f"- Book ID: {book_id}",
        f"- Title: {title}",
        f"- Chapter: {chapter_number}",
        "",
    ]

    for heading, relative_path in YAML_FILES:
        sections.extend(_fenced_section(root, heading, relative_path, "yaml"))

    for heading, relative_path in JSON_FILES:
        sections.extend(_fenced_section(root, heading, relative_path, "json"))

    sections.extend(_knowledge_references())
    sections.extend(
        [
            "## Agent Handoff Instructions",
            "",
            "- Treat book-local canon as truth.",
            "- Use shared knowledge as guidance, not as overriding canon.",
            "- List assumptions and proposed canon changes separately.",
            "- Major canon or state changes require human approval.",
            "- Plan and draft only the requested chapter.",
            "",
        ]
    )

    return "\n".join(sections)


def write_context(book_id: str, chapter_number: int, output_path: Path) -> Path:
    context = build_context(book_id, chapter_number)
    write_text(output_path, context)
    return output_path


def _read_title(root: Path) -> str:
    book_yaml = root / "book.yaml"
    if not book_yaml.exists():
        return root.name
    for line in read_text(book_yaml).splitlines():
        if line.startswith("title:"):
            return line.split(":", 1)[1].strip().strip('"') or root.name
    return root.name


def _fenced_section(root: Path, heading: str, relative_path: str, fence: str) -> list[str]:
    path = root / relative_path
    content = read_text(path) if path.exists() else f"Missing file: {relative_path}\n"
    return [
        f"## {heading}",
        "",
        f"Source: `{relative_path}`",
        "",
        f"```{fence}",
        content.rstrip(),
        "```",
        "",
    ]


def _knowledge_references() -> list[str]:
    lines = ["## Shared Knowledge References", ""]
    if not KNOWLEDGE_DIR.exists():
        lines.extend(["No shared knowledge directory found.", ""])
        return lines

    for path in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        lines.append(f"- `{path.relative_to(KNOWLEDGE_DIR).as_posix()}`")
    lines.append("")
    return lines
