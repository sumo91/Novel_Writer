import json
import hashlib
from dataclasses import dataclass
from pathlib import Path

from engine.io_utils import read_json
from engine.io_utils import read_yaml
from engine.io_utils import write_yaml
from engine.paths import books_dir

BOOKS_DIR = books_dir()
ALLOWED_STATUSES = {"open", "approved", "rejected", "deferred"}


class PendingApprovalNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class PendingApproval:
    id: str
    text: str
    source_chapters: tuple[int, ...]
    sources: tuple[str, ...]
    variants: tuple[str, ...]
    status: str = "open"


NORMALIZATION_RULES = (
    (
        "逆光系统代价方向：信任资源消耗、授权人风险、反制窗口缩短。",
        (
            "逆光系统代价",
            "Define the cost or limitation of the 逆光 system",
            "Define system cost",
        ),
    ),
    (
        "曜石资本账号 obsidian_capital_he01 仅作为线索，不能直接证明主谋。",
        (
            "obsidian_capital_he01",
            "Keep曜石资本账号 as a clue",
            "曜石资本复核账号",
        ),
    ),
    (
        "秦暮雨只读权限来源与授权边界需持续明确。",
        ("秦暮雨的只读权限来源", "Clarify秦暮雨的只读权限来源"),
    ),
    (
        "秦暮雨是风险共同体盟友，但不是无条件私人盟友。",
        ("风险共同体盟友", "风险共同体"),
    ),
    (
        "event_control_review 作为中间审批节点继续追踪。",
        ("event_control_review",),
    ),
    (
        "追溯确认作为当前融资局与旧案的结构性相似线索。",
        ("追溯确认",),
    ),
    (
        "CP-L-02 作为早于何盛的长期资本项目库钩子。",
        ("CP-L-02 作为早于何盛",),
    ),
    (
        "宋启明仍然存活且不在现有名单里的匿名消息作为下一阶段入口。",
        ("宋启明仍然存活",),
    ),
)


def collect_pending_approvals(book_id: str) -> list[PendingApproval]:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")
    return collect_pending_approvals_from_root(root)


def collect_pending_approvals_from_root(root: Path) -> list[PendingApproval]:
    collected: dict[str, dict[str, set]] = {}

    state_path = root / "state" / "current_state.json"
    if state_path.exists():
        state = read_json(state_path)
        chapter = state.get("current_chapter")
        for approval in state.get("pending_approvals", []):
            _add(collected, approval, chapter, "state/current_state.json")

    change_log_path = root / "state" / "change_log.jsonl"
    if change_log_path.exists():
        for line in change_log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            chapter = entry.get("chapter")
            source = f"state/change_log.jsonl:chapter_{chapter}"
            for approval in entry.get("pending_approvals", []):
                _add(collected, approval, chapter, source)

    return [
        PendingApproval(
            id=_approval_id(text),
            text=text,
            source_chapters=tuple(sorted(item["chapters"])),
            sources=tuple(sorted(item["sources"])),
            variants=tuple(sorted(item["variants"])),
        )
        for text, item in sorted(collected.items(), key=lambda pair: pair[0])
    ]


def render_pending_approvals(book_id: str) -> str:
    approvals = collect_pending_approvals(book_id)
    lines = [
        "# Pending Approvals",
        "",
        "| Approval | Status | Source Chapters | Variants | Sources |",
        "| --- | --- | --- | --- | --- |",
    ]
    existing = _existing_approvals_by_id(BOOKS_DIR / book_id / "state" / "pending_approvals.yaml")
    for approval in approvals:
        chapters = ", ".join(str(chapter) for chapter in approval.source_chapters)
        variants = "<br>".join(approval.variants)
        sources = "<br>".join(approval.sources)
        status = existing.get(approval.id, {}).get("status", approval.status)
        lines.append(
            f"| {approval.id} {approval.text} | {status} | {chapters} | {variants} | {sources} |"
        )
    return "\n".join(lines) + "\n"


def sync_pending_approvals(book_id: str) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")
    approvals = collect_pending_approvals_from_root(root)
    output = root / "state" / "pending_approvals.yaml"
    existing = _existing_approvals_by_id(output)
    write_yaml(
        output,
        {
            "approvals": [
                _merge_existing_approval(
                    {
                        "id": approval.id,
                        "status": approval.status,
                        "text": approval.text,
                        "source_chapters": list(approval.source_chapters),
                        "variants": list(approval.variants),
                        "sources": list(approval.sources),
                    },
                    existing.get(approval.id, {}),
                )
                for approval in approvals
            ]
        },
    )
    return output


def update_pending_approval(
    book_id: str,
    approval_id: str,
    *,
    status: str,
    note: str | None = None,
) -> Path:
    if status not in ALLOWED_STATUSES:
        raise ValueError(
            "Pending approval status must be open, approved, rejected, or deferred."
        )

    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    registry_path = root / "state" / "pending_approvals.yaml"
    if not registry_path.exists():
        sync_pending_approvals(book_id)

    registry = read_yaml(registry_path)
    approvals = registry.get("approvals")
    if not isinstance(approvals, list):
        raise ValueError("Pending approvals registry must contain an approvals list.")

    for approval in approvals:
        if isinstance(approval, dict) and approval.get("id") == approval_id:
            approval["status"] = status
            if note is not None:
                approval["note"] = note
            write_yaml(registry_path, registry)
            return registry_path

    raise PendingApprovalNotFoundError(f"Pending approval not found: {approval_id}")


def batch_update_pending_approvals(
    book_id: str,
    updates: list[dict[str, object]],
) -> Path:
    root = BOOKS_DIR / book_id
    if not root.exists():
        raise FileNotFoundError(f"Missing book project: {book_id}")

    registry_path = root / "state" / "pending_approvals.yaml"
    if not registry_path.exists():
        sync_pending_approvals(book_id)

    registry = read_yaml(registry_path)
    approvals = registry.get("approvals")
    if not isinstance(approvals, list):
        raise ValueError("Pending approvals registry must contain an approvals list.")

    by_id = {
        approval["id"]: approval
        for approval in approvals
        if isinstance(approval, dict) and isinstance(approval.get("id"), str)
    }

    for update in updates:
        if not isinstance(update, dict):
            raise ValueError("Each pending approval update must be a mapping.")
        approval_id = update.get("id")
        if not isinstance(approval_id, str):
            raise ValueError("Each pending approval update requires an id.")
        status = update.get("status")
        if status not in ALLOWED_STATUSES:
            raise ValueError(
                "Pending approval status must be open, approved, rejected, or deferred."
            )
        if approval_id not in by_id:
            raise PendingApprovalNotFoundError(
                f"Pending approval not found: {approval_id}"
            )

    for update in updates:
        approval = by_id[str(update["id"])]
        approval["status"] = update["status"]
        note = update.get("note")
        if note is not None:
            approval["note"] = str(note)

    write_yaml(registry_path, registry)
    return registry_path


def _add(
    collected: dict[str, dict[str, set]],
    approval: object,
    chapter: object,
    source: str,
) -> None:
    text = str(approval).strip()
    if not text:
        return
    canonical = _canonical_text(text)
    item = collected.setdefault(
        canonical,
        {"chapters": set(), "sources": set(), "variants": set()},
    )
    if isinstance(chapter, int):
        item["chapters"].add(chapter)
    item["sources"].add(source)
    item["variants"].add(text)


def _canonical_text(text: str) -> str:
    for canonical, needles in NORMALIZATION_RULES:
        if any(needle in text for needle in needles):
            return canonical
    return text


def _approval_id(text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return f"pa_{digest}"


def _existing_approvals_by_id(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    registry = read_yaml(path)
    approvals = registry.get("approvals")
    if not isinstance(approvals, list):
        return {}
    return {
        approval["id"]: approval
        for approval in approvals
        if isinstance(approval, dict) and isinstance(approval.get("id"), str)
    }


def _merge_existing_approval(
    approval: dict[str, object],
    existing: dict[str, object],
) -> dict[str, object]:
    status = existing.get("status")
    if status in ALLOWED_STATUSES:
        approval["status"] = status

    note = existing.get("note")
    if isinstance(note, str) and note:
        approval["note"] = note

    return approval
