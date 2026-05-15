from engine.io_utils import read_yaml, write_json
from engine.paths import book_path, project_root


def test_project_root_returns_repository_root():
    root = project_root()

    assert root.name == "Novel_Writer"
    assert (root / "pyproject.toml").exists()


def test_book_path_returns_path_under_books():
    assert book_path("demo") == project_root() / "books" / "demo"


def test_read_yaml_returns_empty_dict_for_empty_file(tmp_path):
    yaml_path = tmp_path / "empty.yaml"
    yaml_path.write_text("", encoding="utf-8")

    assert read_yaml(yaml_path) == {}


def test_write_json_creates_parent_directories(tmp_path):
    json_path = tmp_path / "nested" / "data.json"

    write_json(json_path, {"ok": True})

    assert json_path.exists()
    assert json_path.read_text(encoding="utf-8").strip() == '{\n  "ok": true\n}'
