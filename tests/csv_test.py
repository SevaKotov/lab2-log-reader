
import pytest

from streamstats.errors import Invalid_Event
from streamstats.errors import Invalid_Path
from streamstats.models import Stats
from streamstats.parsers import csv_parser


def test_csv_valid(tmp_path):
    """Валидный CSV: все строки распарсены."""
    p = tmp_path / "events.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "2024-05-01T10:00:00Z,INFO,auth,hello\n"
        "2024-05-01T10:01:00Z,ERROR,db,fail\n",
        encoding="utf-8",
    )

    stats = Stats()
    events = list(csv_parser([p], skip_error=False, stats=stats))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[1].source == "db"


def test_csv_empty_file(tmp_path):
    """Пустой файл — ноль событий, без падения."""
    p = tmp_path / "empty.csv"
    p.write_text(
        "timestamp,level,source,message\n",
        encoding="utf-8",
    )

    stats = Stats()
    events = list(csv_parser([p], skip_error=False, stats=stats))

    assert events == []


def test_csv_bad_line_strict(tmp_path):
    """Битая строка без skip_invalid — Invalid_Event."""
    p = tmp_path / "bad.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "2024-05-01T10:00:00Z,FATAL,db,fail\n",
        encoding="utf-8",
    )

    stats = Stats()
    with pytest.raises(Invalid_Event):
        list(csv_parser([p], skip_error=False, stats=stats))


def test_csv_bad_line_skipped(tmp_path, caplog):
    """Битая строка с skip_error=True — пропущена, WARNING в логе"""
    p = tmp_path / "bad.csv"
    p.write_text(
        "timestamp,level,source,message\n"
        "2024-05-01T10:00:00Z,FATAL,db,fail\n"
        "2024-05-01T10:01:00Z,INFO,auth,ok\n",
        encoding="utf-8",
    )

    stats = Stats()
    events = list(csv_parser([p], skip_error=True, stats=stats))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert "WARNING" in caplog.text


def test_csv_missing_file(tmp_path):
    """Несуществующий файл — Invalid_Path."""
    stats = Stats()
    with pytest.raises(Invalid_Path):
        list(csv_parser(
            [tmp_path / "no_such.csv"],
            skip_error=False,
            stats=stats,
        ))
