from collections.abc import Iterable, Iterator
from typing import Optional, Self, TypeVar, Generic, NamedTuple, cast

from ._common import make_maybe_weak
from ._common.weakref import WeakRefCallback
from ._events import (
    OptionalMaybeWeak,
    IterableNewIteratorRetrievedEvent,
    IteratorAdvancedEvent,
    IteratorExhaustedEvent,
)
from ._recorder import EventsRecorder

T = TypeVar('T')

class RecordMaybeWeakObjectOptions(NamedTuple, Generic[T]):
    weak: bool
    weak_callback: Optional[WeakRefCallback[T]] = None

class RecordMaybeWeakIterableOptions(RecordMaybeWeakObjectOptions[Iterable[T]]):
    @classmethod
    def create(
        cls, *, weak: bool = True, weak_callback: Optional[WeakRefCallback[Iterable[T]]] = None,
    ) -> Self:
        return cls(weak=weak, weak_callback=weak_callback)

class RecordMaybeWeakIteratorOptions(RecordMaybeWeakObjectOptions[Iterator[T]]):
    @classmethod
    def create(
        cls, *, weak: bool = False, weak_callback: Optional[WeakRefCallback[Iterator[T]]] = None,
    ) -> Self:
        return cls(weak=weak, weak_callback=weak_callback)

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
        self._record_iterable_options: Optional[RecordMaybeWeakIterableOptions[T]] = (
            record_iterable_options
        )
        self._record_requested_iterators_options: Optional[RecordMaybeWeakIteratorOptions[T]] = (
            record_requested_iterators_options
        )
    @property
    def iterable(self) -> Iterable[T]:
        return self._iterable
    def _get_iterable_to_record(self) -> OptionalMaybeWeak[Iterable[T]]:
        return (
            make_maybe_weak(
                self._iterable,
                weak=self._record_iterable_options.weak,
                weak_callback=self._record_iterable_options.weak_callback,
            )
            if self._record_iterable_options is not None
            else None
        )
    def _get_requested_iterator_to_record(
        self, it: Iterator[T],
    ) -> OptionalMaybeWeak[Iterator[T]]:
        return (
            make_maybe_weak(
                it,
                weak=self._record_requested_iterators_options.weak,
                weak_callback=self._record_requested_iterators_options.weak_callback,
            )
            if self._record_requested_iterators_options is not None
            else None
        )
    def __iter__(self) -> Iterator[T]:
        it = iter(self._iterable)
        self._recorder.record_event(
            IterableNewIteratorRetrievedEvent(
                self._get_iterable_to_record(), self._get_requested_iterator_to_record(it),
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
        self._record_iterator_options: Optional[RecordMaybeWeakIteratorOptions[T]] = (
            record_iterator_options
        )
    @property
    def iterator(self) -> Iterator[T]:
        return self._iterator
    def _get_iterator_to_record(self) -> OptionalMaybeWeak[Iterator[T]]:
        return (
            make_maybe_weak(
                self._iterator,
                weak=self._record_iterator_options.weak,
                weak_callback=self._record_iterator_options.weak_callback,
            )
            if self._record_iterator_options is not None
            else None
        )
    def _get_requested_iterator_to_record(
        self, it: Iterator[T],
    ) -> OptionalMaybeWeak[Iterator[T]]:
        return (
            make_maybe_weak(
                it,
                weak=self._record_iterator_options.weak,
                weak_callback=self._record_iterator_options.weak_callback,
            )
            if self._record_iterator_options is not None
            else None
        )
    def __iter__(self) -> Iterator[T]:
        self._recorder.record_event(IterableNewIteratorRetrievedEvent(
            # XXX: cast??
            cast(OptionalMaybeWeak[Iterable[T]], self._get_iterator_to_record()),
            self._get_requested_iterator_to_record(self._iterator),
        ))
        return self
    def __next__(self) -> T:
        try:
            value = next(self._iterator)
        except StopIteration as exc:
            self._recorder.record_event(
                IteratorExhaustedEvent(self._get_iterator_to_record(), exc)
            )
            raise
        self._recorder.record_event(IteratorAdvancedEvent(self._get_iterator_to_record(), value))
        return value
