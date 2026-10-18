from .models import Stats
from .parsers import csv_parser, json_parser


def analyze_csv(data: list, stats: Stats, skip_error: bool) -> None:
    """Анализ csv файла"""
    for event in csv_parser(data, skip_error):
        stats.add_event(event)

def analyze_json(data: list, stats: Stats, skip_error: bool) -> None:
    """Анализ json файла"""
    for event in json_parser(data, skip_error):
        stats.add_event(event)