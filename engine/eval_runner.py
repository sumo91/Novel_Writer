import contextlib
import io
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from engine.io_utils import read_yaml, write_json, write_text, write_yaml
from engine.paths import project_root

PROJECT_ROOT = project_root()


def list_eval_suites() -> list[dict[str, Any]]:
    suites_dir = PROJECT_ROOT / "evals" / "suites"
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


def run_eval_suite(suite_id: str) -> dict[str, Any]:
    suite_path = PROJECT_ROOT / "evals" / "suites" / f"{suite_id}.yaml"
    if not suite_path.exists():
        raise FileNotFoundError(f"Missing eval suite: {suite_id}")
    suite = read_yaml(suite_path)
    cases = suite.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError("Eval suite cases must be a list.")

    results = [_run_case(case) for case in cases if isinstance(case, dict)]
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


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case.get("id", "unnamed"))
    steps = case.get("steps")
    if isinstance(steps, list):
        return _run_dynamic_case(case_id, case, steps)

    command = case.get("command", [])
    if not isinstance(command, list):
        return _case_result(case_id, command, 2, "", "command must be a list", ["command must be a list"])

    exit_code, stdout, stderr = _run_cli_command([str(part) for part in command])
    errors = _expectation_errors(case.get("expect", {}), exit_code, stdout, stderr, PROJECT_ROOT)
    return _case_result(case_id, command, exit_code, stdout, stderr, errors)


def _run_cli_command(argv: list[str]) -> tuple[int, str, str]:
    from engine import cli

    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            exit_code = cli.main(argv)
        except SystemExit as exc:
            code = exc.code
            exit_code = code if isinstance(code, int) else 1
    return exit_code, stdout.getvalue(), stderr.getvalue()


def _run_dynamic_case(case_id: str, case: dict[str, Any], steps: list[Any]) -> dict[str, Any]:
    workspace_root = _prepare_workspace(case_id, case.get("workspace", {}))
    step_results = []
    failed = False
    for step in steps:
        if not isinstance(step, dict):
            continue
        if failed:
            step_results.append(_skipped_step_result(step))
            continue
        result = _run_step(step, workspace_root)
        step_results.append(result)
        failed = not result["passed"]

    errors = [error for result in step_results for error in result["errors"] if not result["passed"]]
    return {
        "id": case_id,
        "command": [],
        "exit_code": 1 if errors else 0,
        "passed": not errors,
        "errors": errors,
        "stdout": "\n".join(result["stdout"] for result in step_results if result["stdout"]),
        "stderr": "\n".join(result["stderr"] for result in step_results if result["stderr"]),
        "workspace": workspace_root.relative_to(PROJECT_ROOT).as_posix(),
        "steps": step_results,
    }


def _prepare_workspace(case_id: str, workspace: Any) -> Path:
    workspace_root = PROJECT_ROOT / ".tmp" / "eval_workspaces" / _safe_path_name(case_id)
    if workspace_root.exists():
        shutil.rmtree(workspace_root)
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


def _run_step(step: dict[str, Any], workspace_root: Path) -> dict[str, Any]:
    step_id = str(step.get("id", "unnamed-step"))
    if isinstance(step.get("write_files"), list):
        return _run_write_files_step(step_id, step, workspace_root)

    command = step.get("command", [])
    if not isinstance(command, list):
        return _step_result(step_id, command, 2, "", "command must be a list", ["command must be a list"])
    cwd = workspace_root / str(step.get("cwd", "."))
    completed = subprocess.run(
        [str(part) for part in command],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    errors = _expectation_errors(
        step.get("expect", {}),
        completed.returncode,
        completed.stdout,
        completed.stderr,
        workspace_root,
    )
    return _step_result(
        step_id,
        command,
        completed.returncode,
        completed.stdout,
        completed.stderr,
        errors,
    )


def _run_write_files_step(
    step_id: str,
    step: dict[str, Any],
    workspace_root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    for item in step.get("write_files", []):
        if not isinstance(item, dict) or not item.get("path"):
            errors.append("write_files entries must contain a path")
            continue
        path = workspace_root / str(item["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        if "content" in item:
            path.write_text(str(item["content"]), encoding="utf-8")
        elif "json" in item:
            write_json(path, item["json"])
        elif "yaml" in item:
            write_yaml(path, item["yaml"])
        else:
            errors.append(f"write_files entry missing content/json/yaml: {item['path']}")
    errors.extend(_expectation_errors(step.get("expect", {}), 0, "", "", workspace_root))
    return _step_result(step_id, [], 0 if not errors else 1, "", "", errors)


def _skipped_step_result(step: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(step.get("id", "unnamed-step")),
        "command": step.get("command", []),
        "exit_code": 0,
        "passed": False,
        "skipped": True,
        "errors": ["skipped after previous step failed"],
        "stdout": "",
        "stderr": "",
    }


def _step_result(
    step_id: str,
    command: Any,
    exit_code: int,
    stdout: str,
    stderr: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "id": step_id,
        "command": command,
        "exit_code": exit_code,
        "passed": not errors,
        "skipped": False,
        "errors": errors,
        "stdout": stdout,
        "stderr": stderr,
    }


def _expectation_errors(
    expect: Any,
    exit_code: int,
    stdout: str,
    stderr: str,
    root: Path,
) -> list[str]:
    if not isinstance(expect, dict):
        return []
    errors: list[str] = []
    expected_exit = expect.get("exit_code")
    if expected_exit is not None and exit_code != expected_exit:
        errors.append(f"exit_code expected {expected_exit}, got {exit_code}")
    for text in _as_list(expect.get("stdout_contains")):
        if str(text) not in stdout:
            errors.append(f"stdout missing: {text}")
    for text in _as_list(expect.get("stderr_contains")):
        if str(text) not in stderr:
            errors.append(f"stderr missing: {text}")
    for text in _as_list(expect.get("stdout_not_contains")):
        if str(text) in stdout:
            errors.append(f"stdout unexpectedly contained: {text}")
    for text in _as_list(expect.get("files_exist")):
        if not (root / str(text)).exists():
            errors.append(f"missing file: {text}")
    for text in _as_list(expect.get("files_not_exist")):
        if (root / str(text)).exists():
            errors.append(f"unexpected file exists: {text}")
    for file_path, required_texts in _as_mapping(expect.get("file_contains")).items():
        content = _read_expected_file(file_path, errors, root)
        if content is None:
            continue
        for text in _as_list(required_texts):
            if str(text) not in content:
                errors.append(f"{file_path} missing text: {text}")
    for file_path, forbidden_texts in _as_mapping(expect.get("file_not_contains")).items():
        content = _read_expected_file(file_path, errors, root)
        if content is None:
            continue
        for text in _as_list(forbidden_texts):
            if str(text) in content:
                errors.append(f"{file_path} unexpectedly contained text: {text}")
    for file_path, maximum in _as_mapping(expect.get("line_count_max")).items():
        content = _read_expected_file(file_path, errors, root)
        if content is None:
            continue
        line_count = len(content.splitlines())
        if line_count > int(maximum):
            errors.append(f"{file_path} line_count expected <= {maximum}, got {line_count}")
    for file_path, minimum in _as_mapping(expect.get("line_count_min")).items():
        content = _read_expected_file(file_path, errors, root)
        if content is None:
            continue
        line_count = len(content.splitlines())
        if line_count < int(minimum):
            errors.append(f"{file_path} line_count expected >= {minimum}, got {line_count}")
    return errors


def _case_result(
    case_id: str,
    command: Any,
    exit_code: int,
    stdout: str,
    stderr: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "id": case_id,
        "command": command,
        "exit_code": exit_code,
        "passed": not errors,
        "errors": errors,
        "stdout": stdout,
        "stderr": stderr,
    }


def _write_reports(report: dict[str, Any]) -> None:
    output_dir = PROJECT_ROOT / "reports" / "evals"
    suite_id = report["suite_id"]
    write_json(output_dir / f"{suite_id}.json", report)
    write_text(output_dir / f"{suite_id}.md", _render_markdown_report(report))


def _render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# Eval Suite: {report['suite_id']}",
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
        lines.append(f"- {marker}: {case['id']}")
        for error in case["errors"]:
            lines.append(f"  - {error}")
        for step in case.get("steps", []):
            step_marker = "PASS" if step["passed"] else "FAIL"
            if step.get("skipped"):
                step_marker = "SKIP"
            lines.append(f"  - {step_marker}: {step['id']}")
            for error in step["errors"]:
                lines.append(f"    - {error}")
    lines.append("")
    return "\n".join(lines)


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _read_expected_file(file_path: str, errors: list[str], root: Path) -> str | None:
    path = root / str(file_path)
    if not path.exists():
        errors.append(f"missing file: {file_path}")
        return None
    return path.read_text(encoding="utf-8")


def _safe_path_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in "-_" else "_" for char in value)
