import csv
import json
import logging

from .errors import Invalid_Event, Invalid_Path, InvalidTimestampError
from .models import LEVELS, Event

logger = logging.getLogger(__name__)


def validation(num: int, info: dict, path: str, skip_error: bool) -> bool:
    """Валидация события. Возвращает True, если событие валидное"""
    if info.get("level") not in LEVELS:
        if skip_error:
            logger.warning(f"WARNING: {path}:{num}: invalid level: {info.get('level')!r}")
            return False
        raise Invalid_Event(f"{path}:{num}: invalid level: {info.get('level')!r}")

    if not info.get("source"):
        if skip_error:
            logger.warning(f"WARNING: {path}:{num}: empty source")
            return False
        raise Invalid_Event(f"{path}:{num}: empty source")

    return True


def csv_parser(data: list, skip_error: bool):
    """Читает CSV-файлы построчно и отдаёт Event"""
    for path in data:
        try:
            with path.open(newline="", encoding="utf-8") as file:
                # Проверка на заголовок
                first_line = file.readline()
                file.seek(0)
                if "timestamp" in first_line:
                    reader = csv.DictReader(file)
                else:
                    reader = csv.DictReader(
                        file,
                        fieldnames=["timestamp", "level", "source", "message"],
                    )
                count = 0
                for num, line in enumerate(reader, start=2):
                    count += 1
                    if not line:
                        continue
                    if not validation(num, line, str(path), skip_error):
                        continue
                    try:
                        yield Event.from_dict(line)
                    except (Invalid_Event, InvalidTimestampError, ValueError) as e:
                        if skip_error:
                            logger.warning(f"WARNING: {path}:{num}: {e}")
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


def json_parser(data: list, skip_error: bool):
    """Читает JSONL-файлы построчно и отдаёт Event."""
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
                            continue
                        raise Invalid_Event(f"{path}:{num}: {e}") from e

                    if not validation(num, event_dict, str(path), skip_error):
                        continue

                    try:
                        yield Event.from_dict(event_dict)
                    except (Invalid_Event, InvalidTimestampError, ValueError) as e:
                        if skip_error:
                            logger.warning(f"WARNING: {path}:{num}: {e}")
                            continue
                        raise Invalid_Event(f"{path}:{num}: {e}") from e

                if count == 0:
                    logger.warning(f"WARNING: {path} is empty")

        except FileNotFoundError:
            raise Invalid_Path(f"Invalid path: {path}")
        except PermissionError:
            raise Invalid_Path(f"No access to file: {path}")
        except OSError as e:
            raise Invalid_Path(f"Can't open {path}: {e}")