import csv
import json
import logging

from .errors import InvalidTimestampError
from .errors import Invalid_Event
from .errors import Invalid_Path
from .models import LEVELS
from .models import Event
from .models import Stats

logger = logging.getLogger(__name__)


def validation(num: int, info: dict, path: str, skip_error: bool, stats: Stats) -> bool:
    """Валидация события, возвращает True, если событие валидное"""
    if not isinstance(info, dict):
        if skip_error:
            logger.warning(f"WARNING: {path}:{num}: event must be an object")
            stats.skip_invalid += 1
            return False
        raise Invalid_Event(f"{path}:{num}: event must be an object")

    required_fields = ["timestamp", "level", "source", "message"]

    for field in required_fields:
        if field not in info:
            if skip_error:
                logger.warning(f"WARNING: {path}:{num}: missing required field: {field}")
                stats.skip_invalid += 1
                return False
            raise Invalid_Event(f"{path}:{num}: missing required field: {field}")

    if info.get("level") not in LEVELS:
        if skip_error:
            logger.warning(f"WARNING: {path}:{num}: invalid level: {info.get('level')!r}")
            stats.skip_invalid += 1
            return False
        else:
            raise Invalid_Event(f"{path}:{num}: invalid level: {info.get('level')!r}")

    if not isinstance(info["timestamp"], str) or not info["timestamp"].strip():
        if skip_error:
            logger.warning(f"WARNING: {path}:{num}: timestamp must be a non-empty string")
            stats.skip_invalid += 1
            return False
        raise Invalid_Event(f"{path}:{num}: timestamp must be a non-empty string")

    if not isinstance(info.get("source"), str) or len(info.get("source").strip()) == 0:
        if skip_error:
            logger.warning(f"WARNING: {path}:{num}: empty source")
            stats.skip_invalid += 1
            return False
        else:
            raise Invalid_Event(f"{path}:{num}: empty source")
    if not isinstance(info.get("message"), str):
        if skip_error:
            logger.warning(f"WARNING: {path}:{num}: not str message")
            stats.skip_invalid += 1
            return False
        else:
            raise Invalid_Event(f"{path}:{num}: not str message")
    return True

def csv_parser(data: list, skip_error: bool, stats: Stats):
    """Читает CSV-файлы построчно и отдаёт Event"""
    for path in data:
        try:
            with path.open(newline="", encoding="utf-8") as file:
                first_line = file.readline()
                file.seek(0)
                header = next(csv.reader([first_line]), [])
                header = [column.strip() for column in header]

                expected_header = ["timestamp", "level", "source", "message"]
                has_header = header == expected_header
                if has_header:
                    reader = csv.DictReader(file)
                else:
                    reader = csv.DictReader(
                        file,
                        fieldnames=["timestamp", "level", "source", "message"],
                    )
                count = 0

                start_num = 2 if has_header else 1
                for num, line in enumerate(reader, start=start_num):
                    count += 1
                    if not line:
                        continue
                    if not validation(num, line, str(path), skip_error, stats):
                        continue
                    try:
                        yield Event.from_dict(line)
                    except (Invalid_Event, InvalidTimestampError, ValueError) as e:
                        if skip_error:
                            logger.warning(f"WARNING: {path}:{num}: {e}")
                            stats.skip_invalid += 1
                            continue
                        raise Invalid_Event(f"{path}:{num}: {e}") from e

                if count == 0:
                    logger.warning(f"WARNING: {path} is empty")

        except FileNotFoundError as e:
            raise Invalid_Path(f"Invalid path: {path}") from e
        except PermissionError as e:
            raise Invalid_Path(f"No access to file: {path}") from e
        except OSError as e:
            raise Invalid_Path(f"Can't open {path}: {e}") from e


def json_parser(data: list, skip_error: bool, stats: Stats):
    """Читает JSONL-файлы построчно и отдаёт Event"""
    for path in data:
        try:
            with path.open(encoding="utf-8") as file:
                count = 0
                for num, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    count += 1
                    try:
                        event_dict = json.loads(line)
                    except json.JSONDecodeError as e:
                        if skip_error:
                            logger.warning(f"WARNING: {path}:{num}: {e}")
                            stats.skip_invalid += 1
                            continue
                        raise Invalid_Event(f"{path}:{num}: {e}") from e

                    if not validation(num, event_dict, str(path), skip_error, stats):
                        continue
                    try:
                        yield Event.from_dict(event_dict)
                    except (Invalid_Event, InvalidTimestampError, ValueError) as e:
                        if skip_error:
                            logger.warning(f"WARNING: {path}:{num}: {e}")
                            stats.skip_invalid += 1
                            continue
                        raise Invalid_Event(f"{path}:{num}: {e}") from e

                if count == 0:
                    logger.warning(f"WARNING: {path} is empty")

        except FileNotFoundError as e:
            raise Invalid_Path(f"Invalid path: {path}") from e
        except PermissionError as e:
            raise Invalid_Path(f"No access to file: {path}") from e
        except OSError as e:
            raise Invalid_Path(f"Can't open {path}: {e}") from e