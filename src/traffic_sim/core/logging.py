from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Event:
    time_s: float
    type: str
    vehicle_ids: List[int]
    info: dict


class EventLogger:
    def __init__(self):
        self.events: List[Event] = []

    def log(self, event: Event) -> None:
        self.events.append(event)


