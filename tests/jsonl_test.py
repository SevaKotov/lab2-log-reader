import pytest

from streamstats.errors import Invalid_Event
from streamstats.errors import Invalid_Path
from streamstats.parsers import json_parser


def test_jsonl_valid(tmp_path):
    """Валидный JSONL: все строки распарсены."""
    p = tmp_path / "events.jsonl"
    p.write_text(
        '{"timestamp":"2024-05-01T10:00:00Z","level":"INFO","source":"auth","message":"ok"}\n'
        '{"timestamp":"2024-05-01T10:01:00Z","level":"ERROR","source":"db","message":"fail"}\n',
        encoding="utf-8",
    )

    events = list(json_parser([p], skip_error=False))

    assert len(events) == 2
    assert events[0].source == "auth"
    assert events[1].level == "ERROR"


def test_jsonl_empty_file(tmp_path):
    """Пустой JSONL — ноль событий."""
    p = tmp_path / "empty.jsonl"
    p.write_text("", encoding="utf-8")

    events = list(json_parser([p], skip_error=False))

    assert events == []


def test_jsonl_bad_json_strict(tmp_path):
    """Битая JSON-строка без skip_invalid — Invalid_Event."""
    p = tmp_path / "bad.jsonl"
    p.write_text("не json\n", encoding="utf-8")

    with pytest.raises(Invalid_Event):
        list(json_parser([p], skip_error=False))


def test_jsonl_bad_json_skipped(tmp_path, caplog):
    """Битая JSON-строка с skip_error=True — пропущена."""
    p = tmp_path / "bad.jsonl"
    p.write_text(
        "не json\n"
        '{"timestamp":"2024-05-01T10:00:00Z","level":"INFO","source":"auth","message":"ok"}\n',
        encoding="utf-8",
    )

    events = list(json_parser([p], skip_error=True))

    assert len(events) == 1
    assert "WARNING" in caplog.text


def test_jsonl_missing_file(tmp_path):
    """Несуществующий файл — Invalid_Path."""
    with pytest.raises(Invalid_Path):
        list(json_parser([tmp_path / "no_such.jsonl"], skip_error=False))