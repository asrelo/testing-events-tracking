from collections import deque
from collections.abc import Sequence
from threading import Lock

from ._events import AbstractEvent

class EventsRecorder:
    def __init__(self):
        self._events_lock: Lock = Lock()
        self._events: deque[AbstractEvent] = deque()
    def record_event(self, event: AbstractEvent) -> None:
        with self._events_lock:
            self._events.append(event)
    def retrieve_events(self) -> Sequence[AbstractEvent]:
        with self._events_lock:
            ret = list(self._events)
            self._events.clear()
        return ret
