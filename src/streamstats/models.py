import datetime

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class Event:
    def __init__(self, timestamp, level, source, message):
        """Создание объекта Event"""
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message

    @classmethod
    def from_dict(cls, di: dict):
        """подготовка данных для перевода в Event"""
        ts = datetime.datetime.fromisoformat(di["timestamp"])
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=datetime.UTC)
        else:
            ts = ts.astimezone(datetime.UTC)
        return cls(
            timestamp=ts,
            level=di["level"],
            source=di["source"],
            message=di["message"]
        )

class Stats:
    """Класс для статистики"""
    def __init__(self):
        self.total = 0
        self.level_amount = {"DEBUG":0, "INFO":0, "WARNING":0, "ERROR":0, "CRITICAL":0}
        self.sources = []
        self.top_five = []
        self.f_timestamp = None
        self.l_timestamp = None
        self.skip_invalid = 0

    def add_event(self, event: Event) -> None:
        """метод класса для обработки ивента"""
        self.total += 1
        self.level_amount[event.level]+=1
        self.sources.append(event.source)

        if event.level == "ERROR" or event.level == "CRITICAL":
            self.top_five.append(event.source)

        if self.f_timestamp is None or event.timestamp < self.f_timestamp:
            self.f_timestamp = event.timestamp
        if self.l_timestamp is None or event.timestamp > self.l_timestamp:
            self.l_timestamp = event.timestamp
