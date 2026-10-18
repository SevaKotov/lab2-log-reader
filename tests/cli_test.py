import json

from streamstats.__main__ import main


def test_cli_success_csv(tmp_path):
    """Успешный запуск CSV: код 0, отчёт с правильными цифрами"""
    events = tmp_path / "events.csv"
    events.write_text(
        "timestamp,level,source,message\n"
        "2024-05-01T10:00:00Z,INFO,auth,hello\n"
        "2024-05-01T10:01:00Z,ERROR,db,fail\n",
        encoding="utf-8",
    )
    report = tmp_path / "report.json"

    code = main(["analyze", str(events), "--format", "csv", "--output", str(report)])

    assert code == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["total_events"] == 2
    assert data["levels"]["INFO"] == 1
    assert data["levels"]["ERROR"] == 1


def test_cli_bad_line_returns_2(tmp_path):
    """Битая строка без --skip-invalid: код 2, отчёт не создан"""
    events = tmp_path / "bad.csv"
    events.write_text(
        "timestamp,level,source,message\n"
        "2024-05-01T10:00:00Z,FATAL,db,fail\n",
        encoding="utf-8",
    )
    report = tmp_path / "report.json"

    code = main(["analyze", str(events), "--format", "csv", "--output", str(report)])

    assert code == 2
    assert not report.exists()


def test_cli_skip_invalid_and_multiple_files(tmp_path):
    """--skip-invalid + два файла: объединение, пропуск, счётчик."""
    f1 = tmp_path / "a.jsonl"
    f1.write_text(
        '{"timestamp":"2024-05-01T10:00:00Z","level":"INFO","source":"auth","message":"ok"}\n'
        '{"timestamp":"2024-05-01T10:01:00Z","level":"FATAL","source":"db","message":"bad"}\n',
        encoding="utf-8",
    )
    f2 = tmp_path / "b.jsonl"
    f2.write_text(
        '{"timestamp":"2024-05-01T10:02:00Z","level":"ERROR","source":"db","message":"fail"}\n',
        encoding="utf-8",
    )
    report = tmp_path / "report.json"

    code = main([
        "analyze", str(f1), str(f2),
        "--format", "jsonl",
        "--skip-invalid",
        "--output", str(report),
    ])

    assert code == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["total_events"] == 2
    assert data["sources"] == {"auth": 1, "db": 1}