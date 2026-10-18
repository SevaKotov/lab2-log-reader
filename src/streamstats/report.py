import csv
import json
from collections import Counter

from .analysis import Stats


def build_report(stats: Stats) -> dict:
    """Собирает словарь-отчет из stats"""
    top = Counter(stats.top_five).most_common(5)
    top_list = [{"source": src, "count": cnt} for src, cnt in top]

    report = {
        "total_events": stats.total,
        "levels":dict(stats.level_amount),
        "first_timestamp": stats.f_timestamp.isoformat() if stats.f_timestamp else None,
    "last_timestamp": stats.l_timestamp.isoformat() if stats.l_timestamp else None,
        "sources": dict(Counter(stats.sources)),
        "top_error_sources": top_list
    }

    return report

def write_json(report: dict, output_path: str) -> None:
    """Сохраняет словарь в файл"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

def write_csv(report: dict, output_path: str) -> None:
    """Сохраняет готовый отчет в CSV"""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])

        writer.writerow(["total_events", report["total_events"]])
        writer.writerow(["first_timestamp", report["first_timestamp"]])
        writer.writerow(["last_timestamp", report["last_timestamp"]])

        for level, count in report["levels"].items():
            writer.writerow([f"level_{level}", count])

        for source, count in report["sources"].items():
            writer.writerow([f"source_{source}", count])

        for item in report["top_error_sources"]:
            writer.writerow([f"top_error_{item['source']}", item["count"]])
