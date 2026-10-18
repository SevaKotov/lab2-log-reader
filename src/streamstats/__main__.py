import argparse
import sys

from pathlib import Path

from streamstats.report import build_report
from streamstats.report import write_csv
from streamstats.report import write_json

from .analysis import Stats
from .analysis import analyze_csv
from .analysis import analyze_json
from .errors import Invalid_Format
from .errors import Stream_Stats_Error


def build_parser()->argparse.ArgumentParser:
    """Парсер"""
    parser = argparse.ArgumentParser(
        prog="streamstats",
        description="Stream event files and build a reports"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze one or more event files")
    analyze.add_argument("inputs", nargs="+", type=Path, metavar="Input", help="One or more input csv or/and jsonl files")
    analyze.add_argument("--format", choices=["csv", "jsonl"], required=True, help="Input file format")
    analyze.add_argument("--output", required=True, type=Path, metavar="REPORT.json", help="Path to write a json report")
    analyze.add_argument("--skip-invalid", action="store_true", help="Skip invalid lines instead of falling")

    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            stats = Stats()
            if args.format == "csv":
                analyze_csv(args.inputs, stats, args.skip_invalid)
            elif args.format == "jsonl":
                analyze_json(args.inputs, stats, args.skip_invalid)
            else:
                raise Invalid_Format("Invalid input format")
            rp = build_report(stats)
            if args.output.suffix == ".csv":
                write_csv(rp, args.output)
                return 0
            elif args.output.suffix == ".json":
                write_json(rp, args.output)
                return 0
            else:
                raise Invalid_Format("Invalid output format")
    except Stream_Stats_Error as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 2



if __name__== "__main__":
    sys.exit(main())