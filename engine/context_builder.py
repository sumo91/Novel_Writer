from pathlib import Path

from engine.io_utils import read_text, read_yaml, write_text
from engine.paths import books_dir, knowledge_dir

BOOKS_DIR = books_dir()
KNOWLEDGE_DIR = knowledge_dir()

YAML_FILES = [
    ("Story Bible", "canon/novel_bible.yaml"),
    ("Characters", "canon/characters.yaml"),
    ("Master Outline", "outlines/master_outline.yaml"),
    ("Economy", "canon/economy.yaml"),
    ("Factions", "canon/factions.yaml"),
    ("Timeline", "canon/timeline.yaml"),
    ("Character States", "canon/character_states.yaml"),
    ("Open Threads", "canon/open_threads.yaml"),
    ("Resource Ledger", "canon/resource_ledger.yaml"),
    ("Payoff Ledger", "canon/payoff_ledger.yaml"),
    # V3 ledgers are still small; later versions can slice by relevance.
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

    active = _active_outline_paths(root, chapter_number)
    sections.extend(_outline_reference_chain(chapter_number, active))
    for heading, relative_path in YAML_FILES:
        sections.extend(_fenced_section(root, heading, relative_path, "yaml"))
    sections.extend(
        _fenced_section(
            root,
            "Current Volume",
            active["volume"],
            "yaml",
            approval_note=True,
        )
    )
    sections.extend(
        _fenced_section(
            root,
            "Current Arc",
            active["arc"],
            "yaml",
            approval_note=True,
        )
    )
    sections.extend(
        _fenced_section(
            root,
            "Current Unit",
            active["unit"],
            "yaml",
            approval_note=True,
        )
    )
    # Backward-compatible heading kept for existing prompt expectations.
    sections.extend(_fenced_section(root, "Unit Plan", active["unit"], "yaml"))

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


def _active_outline_paths(root: Path, chapter_number: int) -> dict[str, str]:
    return {
        "volume": _first_ranged_yaml(
            root,
            "outlines/volumes",
            chapter_number,
            fallback="outlines/volumes/volume_001.yaml",
        ),
        "arc": _first_ranged_yaml(
            root,
            "outlines",
            chapter_number,
            fallback="outlines/arc_001.yaml",
            glob_pattern="arc_*.yaml",
        ),
        "unit": _first_ranged_yaml(
            root,
            "outlines/units",
            chapter_number,
            fallback="outlines/units/unit_0001.yaml",
        ),
    }


def _first_ranged_yaml(
    root: Path,
    relative_dir: str,
    chapter_number: int,
    fallback: str,
    glob_pattern: str = "*.yaml",
) -> str:
    directory = root / relative_dir
    if not directory.exists():
        return fallback
    for path in sorted(directory.glob(glob_pattern)):
        data = read_yaml(path)
        chapter_range = data.get("chapter_range")
        if not isinstance(chapter_range, dict):
            continue
        start = chapter_range.get("start")
        end = chapter_range.get("end")
        if isinstance(start, int) and isinstance(end, int) and start <= chapter_number <= end:
            return path.relative_to(root).as_posix()
    return fallback


def _outline_reference_chain(chapter_number: int, active: dict[str, str]) -> list[str]:
    volume_id = Path(active["volume"]).stem
    arc_id = Path(active["arc"]).stem
    unit_id = Path(active["unit"]).stem
    return [
        "## Outline Reference Chain",
        "",
        f"master -> {volume_id} -> {arc_id} -> {unit_id} -> chapter_{chapter_number:04d}",
        "",
    ]


def _fenced_section(
    root: Path,
    heading: str,
    relative_path: str,
    fence: str,
    approval_note: bool = False,
) -> list[str]:
    path = root / relative_path
    content = read_text(path) if path.exists() else f"Missing file: {relative_path}\n"
    lines = [
        f"## {heading}",
        "",
        f"Source: `{relative_path}`",
        "",
    ]
    if approval_note:
        note = _approval_note(path)
        if note:
            lines.extend([note, ""])
    lines.extend(
        [
            f"```{fence}",
            content.rstrip(),
            "```",
            "",
        ]
    )
    return lines


def _approval_note(path: Path) -> str:
    if not path.exists():
        return ""
    data = read_yaml(path)
    approval = data.get("approval") if isinstance(data, dict) else None
    status = approval.get("status") if isinstance(approval, dict) else None
    if status and status != "approved":
        return f"Approval: {status} draft assumption; do not treat as hard canon."
    if status == "approved":
        return "Approval: approved."
    return ""


def _knowledge_references() -> list[str]:
    lines = ["## Shared Knowledge References", ""]
    if not KNOWLEDGE_DIR.exists():
        lines.extend(["No shared knowledge directory found.", ""])
        return lines

    for path in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        lines.append(f"- `{path.relative_to(KNOWLEDGE_DIR).as_posix()}`")
    lines.append("")
    return lines
