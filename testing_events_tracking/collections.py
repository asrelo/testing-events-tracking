from collections.abc import Iterable, Iterator
from typing import Optional, Self, TypeVar, cast

from ._common.weakref import (
    RecordMaybeWeakObjectOptions,
    RecordingObjectConverter,
)
from ._events import (
    OptionalMaybeWeak,
    IterableNewIteratorRetrievedEvent,
    IteratorAdvancedEvent,
    IteratorExhaustedEvent,
)
from ._recorder import EventsRecorder


T = TypeVar('T')


class RecordMaybeWeakIterableOptions(RecordMaybeWeakObjectOptions[Iterable[T]]):

    @classmethod
    def create_default(cls) -> Self:
        return cls.weak()


class RecordMaybeWeakIteratorOptions(RecordMaybeWeakObjectOptions[Iterator[T]]):

    @classmethod
    def create_default(cls) -> Self:
        return cls.strong()


class TrackedIterable(Iterable[T]):

    def __init__(
        self,
        iterable: Iterable[T],
        recorder: EventsRecorder,
        *, record_iterable_options: Optional[RecordMaybeWeakIterableOptions[T]] = None,
        record_requested_iterators_options: Optional[RecordMaybeWeakIteratorOptions[T]] = (
            None
        ),
    ):
        self._iterable: Iterable[T] = iterable
        self._recorder: EventsRecorder = recorder
        self._record_requested_iterators_options: Optional[RecordMaybeWeakIteratorOptions[T]] = (
            record_requested_iterators_options
        )
        self._iterable_recording_converter = RecordingObjectConverter(record_iterable_options)
        self._requested_iterators_recording_converter = (
            RecordingObjectConverter(record_requested_iterators_options)
        )

    @property
    def iterable(self) -> Iterable[T]:
        return self._iterable

    def __iter__(self) -> Iterator[T]:
        it = iter(self._iterable)
        self._recorder.record_event(
            IterableNewIteratorRetrievedEvent(
                self._iterable_recording_converter(self._iterable),
                self._requested_iterators_recording_converter(it),
            )
        )
        return TrackedIterator(
            it, self._recorder, record_iterator_options=self._record_requested_iterators_options,
        )


class TrackedIterator(Iterator[T]):
    def __init__(
        self,
        iterator: Iterator[T],
        recorder: EventsRecorder,
        *, record_iterator_options: Optional[RecordMaybeWeakIteratorOptions[T]] = None,
    ):
        self._iterator: Iterator[T] = iterator
        self._recorder: EventsRecorder = recorder
        self._iterator_recording_converter = RecordingObjectConverter(record_iterator_options)

    @property
    def iterator(self) -> Iterator[T]:
        return self._iterator

    def __iter__(self) -> Iterator[T]:
        self._recorder.record_event(IterableNewIteratorRetrievedEvent(
            # XXX: cast??
            cast(
                OptionalMaybeWeak[Iterable[T]], self._iterator_recording_converter(self._iterator)
            ),
            self._iterator_recording_converter(self._iterator),
        ))
        return self

    def __next__(self) -> T:
        try:
            value = next(self._iterator)
        except StopIteration as exc:
            self._recorder.record_event(
                IteratorExhaustedEvent(self._iterator_recording_converter(self._iterator), exc)
            )
            raise
        self._recorder.record_event(
            IteratorAdvancedEvent(self._iterator_recording_converter(self._iterator), value)
        )
        return value
