import json
import os
import shutil
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from engine.io_utils import read_yaml, write_json, write_text
from engine.paths import project_root

PROJECT_ROOT = project_root()


def list_trace_eval_suites() -> list[dict[str, Any]]:
    suites_dir = PROJECT_ROOT / "evals" / "traces"
    if not suites_dir.exists():
        return []
    suites = []
    for path in sorted(suites_dir.glob("*.yaml")):
        data = read_yaml(path)
        cases = data.get("cases", [])
        suites.append(
            {
                "id": str(data.get("id") or path.stem),
                "description": str(data.get("description", "")),
                "cases": len(cases) if isinstance(cases, list) else 0,
            }
        )
    return suites


LiveRunner = Callable[[dict[str, Any], Path], dict[str, Any]]


def run_trace_eval_suite(
    suite_id: str,
    allow_live: bool = False,
    live_runner: LiveRunner | None = None,
) -> dict[str, Any]:
    suite_path = PROJECT_ROOT / "evals" / "traces" / f"{suite_id}.yaml"
    if not suite_path.exists():
        raise FileNotFoundError(f"Missing trace eval suite: {suite_id}")
    suite = read_yaml(suite_path)
    cases = suite.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError("Trace eval suite cases must be a list.")

    results = [
        _run_case(case, allow_live=allow_live, live_runner=live_runner)
        for case in cases
        if isinstance(case, dict)
    ]
    passed_count = sum(1 for result in results if result["passed"])
    failed_count = len(results) - passed_count
    report = {
        "suite_id": str(suite.get("id") or suite_id),
        "description": str(suite.get("description", "")),
        "generated_at": datetime.now(UTC).isoformat(),
        "passed": failed_count == 0,
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": failed_count,
        },
        "cases": results,
    }
    _write_reports(report)
    return report


def _run_case(
    case: dict[str, Any],
    allow_live: bool = False,
    live_runner: LiveRunner | None = None,
) -> dict[str, Any]:
    case_id = str(case.get("id", "unnamed"))
    mode = str(case.get("mode", "fixture"))
    if mode == "live":
        return _run_live_case(case_id, case, allow_live, live_runner)
    if mode != "fixture":
        return _case_result(
            case_id,
            mode,
            "",
            [],
            [f"unsupported trace eval mode: {mode}"],
        )

    fixture = case.get("fixture", {})
    if not isinstance(fixture, dict):
        fixture = {}
    final_response = str(fixture.get("final_response", ""))
    file_events = _as_file_events(fixture.get("file_events", []))
    errors = _expectation_errors(case.get("expect", {}), final_response, file_events)
    return _case_result(case_id, mode, final_response, file_events, errors)


def _run_live_case(
    case_id: str,
    case: dict[str, Any],
    allow_live: bool,
    live_runner: LiveRunner | None,
) -> dict[str, Any]:
    if not allow_live:
        return _case_result(case_id, "live", "", [], ["live trace eval requires --live"])

    workspace_root = _prepare_live_workspace(case_id, case.get("workspace", {}))
    runner = live_runner or _run_codex_live_case
    run_result = runner(case, workspace_root)
    final_response = str(run_result.get("final_response", ""))
    file_events = _as_file_events(run_result.get("file_events", []))
    errors = []
    exit_code = int(run_result.get("exit_code", 1))
    if exit_code != 0:
        errors.append(f"live runner exit_code expected 0, got {exit_code}")
    errors.extend(_expectation_errors(case.get("expect", {}), final_response, file_events))
    result = _case_result(case_id, "live", final_response, file_events, errors)
    result.update(
        {
            "exit_code": exit_code,
            "stdout": str(run_result.get("stdout", "")),
            "stderr": str(run_result.get("stderr", "")),
            "workspace": workspace_root.relative_to(PROJECT_ROOT).as_posix(),
        }
    )
    return result


def _prepare_live_workspace(case_id: str, workspace: Any) -> Path:
    run_id = f"{_safe_path_name(case_id)}_{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%f')}_{os.getpid()}_{uuid.uuid4().hex[:8]}"
    workspace_root = PROJECT_ROOT / ".tmp" / "trace_eval_workspaces" / run_id
    workspace_root.mkdir(parents=True)
    if isinstance(workspace, dict):
        for relative in _as_list(workspace.get("copy")):
            source = PROJECT_ROOT / str(relative)
            target = workspace_root / str(relative)
            if source.is_dir():
                shutil.copytree(source, target)
            elif source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    return workspace_root


def _run_codex_live_case(case: dict[str, Any], workspace_root: Path) -> dict[str, Any]:
    prompt = _build_live_prompt(case)
    output_path = workspace_root / ".trace_eval_last_message.txt"
    command = [
        _codex_executable(),
        "exec",
        "--json",
        "--ephemeral",
        "--sandbox",
        str(_live_sandbox(case)),
        "--output-last-message",
        str(output_path),
        "--cd",
        str(workspace_root),
        "-",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=workspace_root,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=_live_timeout_seconds(case),
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "final_response": "",
            "file_events": [],
            "stdout": exc.stdout or "",
            "stderr": f"live codex exec timed out after {exc.timeout} seconds",
            "exit_code": 124,
        }
    except OSError as exc:
        return {
            "final_response": "",
            "file_events": [],
            "stdout": "",
            "stderr": f"{exc.__class__.__name__}: {exc}",
            "exit_code": 1,
        }
    final_response = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
    return {
        "final_response": final_response,
        "file_events": _file_events_from_jsonl(completed.stdout),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_code": completed.returncode,
    }


def _codex_executable() -> str:
    for name in ("codex.cmd", "codex.exe", "codex"):
        path = shutil.which(name)
        if path:
            return path
    return "codex"


def _live_timeout_seconds(case: dict[str, Any]) -> int:
    live = case.get("live", {})
    if isinstance(live, dict):
        value = live.get("timeout_seconds")
        if isinstance(value, int) and value > 0:
            return value
    return 120


def _live_sandbox(case: dict[str, Any]) -> str:
    live = case.get("live", {})
    if isinstance(live, dict):
        value = live.get("sandbox")
        if value in {"read-only", "workspace-write", "danger-full-access"}:
            return str(value)
    return "workspace-write"


def _build_live_prompt(case: dict[str, Any]) -> str:
    prompt = str(case.get("prompt", ""))
    guardrail = (
        "This is a trace eval. Follow repository AGENTS.md and the showrunner skill. "
        "Do not create, modify, or delete files unless the prompt explicitly asks for implementation. "
        "If the user asks for raw novel ideation or premature prose, respond conversationally and stop at the required gate. "
        "Answer the user prompt below now."
    )
    return f"{guardrail}\n\nUser prompt:\n{prompt}"


def _file_events_from_jsonl(output: str) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    for line in output.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.extend(_file_events_from_json(item))
    return events


def _file_events_from_json(item: Any) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    if isinstance(item, dict):
        action = _event_action(item)
        path = _event_path(item)
        if action and path:
            events.append({"action": action, "path": _normalize_path(path)})
        for value in item.values():
            events.extend(_file_events_from_json(value))
    elif isinstance(item, list):
        for value in item:
            events.extend(_file_events_from_json(value))
    return events


def _event_action(item: dict[str, Any]) -> str:
    raw = str(item.get("action") or item.get("type") or item.get("kind") or "")
    lowered = raw.lower()
    if any(token in lowered for token in ("create", "write", "add")):
        return "create"
    if any(token in lowered for token in ("modify", "update", "patch", "edit")):
        return "modify"
    if "delete" in lowered or "remove" in lowered:
        return "delete"
    return ""


def _event_path(item: dict[str, Any]) -> str:
    for key in ("path", "file", "filename", "target"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _expectation_errors(
    expect: Any,
    final_response: str,
    file_events: list[dict[str, str]],
) -> list[str]:
    if not isinstance(expect, dict):
        return []
    errors: list[str] = []
    for text in _as_list(expect.get("response_contains")):
        if str(text) not in final_response:
            errors.append(f"response missing: {text}")
    for options in _as_list(expect.get("response_contains_any")):
        option_texts = [str(option) for option in _as_list(options)]
        if option_texts and not any(option in final_response for option in option_texts):
            errors.append(f"response missing any of: {' | '.join(option_texts)}")
    for text in _as_list(expect.get("response_not_contains")):
        if str(text) in final_response:
            errors.append(f"response unexpectedly contained: {text}")

    created_paths = [
        event["path"]
        for event in file_events
        if event.get("action") in {"create", "write"}
    ]
    expected_created = [str(path) for path in _as_list(expect.get("files_created"))]
    for path in expected_created:
        if path not in created_paths:
            errors.append(f"expected file creation missing: {path}")
    if "files_created" in expect:
        for path in created_paths:
            if path not in expected_created:
                errors.append(f"unexpected file creation: {path}")
    for prefix in _as_list(expect.get("files_not_created_under")):
        prefix_text = str(prefix)
        for path in created_paths:
            if path.startswith(prefix_text):
                errors.append(f"unexpected file creation under {prefix_text}: {path}")
    return errors


def _case_result(
    case_id: str,
    mode: str,
    final_response: str,
    file_events: list[dict[str, str]],
    errors: list[str],
) -> dict[str, Any]:
    return {
        "id": case_id,
        "mode": mode,
        "passed": not errors,
        "errors": errors,
        "final_response": final_response,
        "file_events": file_events,
    }


def _write_reports(report: dict[str, Any]) -> None:
    output_dir = PROJECT_ROOT / "reports" / "trace_evals"
    suite_id = report["suite_id"]
    write_json(output_dir / f"{suite_id}.json", report)
    write_text(output_dir / f"{suite_id}.md", _render_markdown_report(report))


def _render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# Trace Eval Suite: {report['suite_id']}",
        "",
        f"- Passed: {report['passed']}",
        f"- Total: {report['summary']['total']}",
        f"- Passed cases: {report['summary']['passed']}",
        f"- Failed cases: {report['summary']['failed']}",
        "",
        "## Cases",
        "",
    ]
    for case in report["cases"]:
        marker = "PASS" if case["passed"] else "FAIL"
        lines.append(f"- {marker}: {case['id']} ({case['mode']})")
        for error in case["errors"]:
            lines.append(f"  - {error}")
    lines.append("")
    return "\n".join(lines)


def _as_file_events(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    events = []
    for item in value:
        if isinstance(item, dict):
            events.append(
                {
                    "action": str(item.get("action", "")),
                    "path": _normalize_path(str(item.get("path", ""))),
                }
            )
    return events


def _normalize_path(path: str) -> str:
    return Path(path).as_posix()


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_path_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in "-_" else "_" for char in value)
