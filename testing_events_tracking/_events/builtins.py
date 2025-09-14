from collections.abc import Iterable, Iterator
from operator import is_, eq
from typing import Optional, Generic, TypeVar, cast

from ._common import (
    OptionalMaybeWeak,
    MATCH_OBJECTS_USE_EQ_DEFAULT,
    match_optional_objects,
    match_optional_maybe_weak_objects,
    EventVerificationStrictness,
    AbstractEvent,
)

T = TypeVar('T')

class IterableRelatedEvent(AbstractEvent, Generic[T]):
    def __init__(self, iterable: OptionalMaybeWeak[Iterable[T]] = None):
        self.iterable: OptionalMaybeWeak[Iterable[T]] = iterable
    def verify(
        self,
        reference_event: 'AbstractEvent',
        *, strictness: EventVerificationStrictness = (
            AbstractEvent._EVENT_VERIFICATION_STRICTNESS_DEFAULT
        ),
    ) -> None:
        super().verify(reference_event, strictness=strictness)
        reference_event = cast(IterableRelatedEvent, reference_event)
        if strictness >= EventVerificationStrictness.STRICT:
            if not match_optional_maybe_weak_objects(
                self.iterable, reference_event.iterable,
                allow_none=(strictness <= EventVerificationStrictness.STRICT),
            ):
                raise ValueError(
                     'Different iterable objects:'
                    f' expected {reference_event.iterable!r}, got {self.iterable!r}'
                )
    def __repr__(self) -> str:
        if type(self) is IterableRelatedEvent:  #pylint: disable=unidiomatic-typecheck
            return f'{type(self).__name__}({self.iterable!r})'
        return super().__repr__()
    def __str__(self) -> str:
        return f'event related to the iterable {self.iterable!r}'

class IterableNewIteratorRetrievedEvent(IterableRelatedEvent[T]):
    def __init__(
        self,
        iterable: OptionalMaybeWeak[Iterable[T]] = None,
        iterator: OptionalMaybeWeak[Iterator[T]] = None,
    ):
        super().__init__(iterable)
        self.iterator: OptionalMaybeWeak[Iterator[T]] = iterator
    def verify(
        self,
        reference_event: 'AbstractEvent',
        *, strictness: EventVerificationStrictness = (
            IterableRelatedEvent._EVENT_VERIFICATION_STRICTNESS_DEFAULT #pylint: disable=protected-access
        ),
    ) -> None:
        super().verify(reference_event, strictness=strictness)
        reference_event = cast(IterableNewIteratorRetrievedEvent, reference_event)
        if strictness >= EventVerificationStrictness.STRICT:
            if not match_optional_maybe_weak_objects(
                self.iterator, reference_event.iterator,
                allow_none=(strictness <= EventVerificationStrictness.STRICT),
            ):
                raise ValueError(
                     'Different iterator objects returned:'
                    f' expected {reference_event.iterator!r}, got {self.iterator!r}'
                )
    def __repr__(self) -> str:
        if type(self) is IterableNewIteratorRetrievedEvent:  #pylint: disable=unidiomatic-typecheck
            return f'{type(self).__name__}({self.iterable!r}, {self.iterator!r})'
        return super().__repr__()
    def __str__(self) -> str:
        return f'new iterator {self.iterator!r} retrieved from the iterable {self.iterable!r}'

class IteratorRelatedEvent(AbstractEvent, Generic[T]):
    def __init__(self, iterator: OptionalMaybeWeak[Iterator[T]] = None):
        self.iterator: OptionalMaybeWeak[Iterator[T]] = iterator
    def verify(
        self,
        reference_event: 'AbstractEvent',
        *, strictness: EventVerificationStrictness = (
            AbstractEvent._EVENT_VERIFICATION_STRICTNESS_DEFAULT
        ),
    ) -> None:
        super().verify(reference_event, strictness=strictness)
        reference_event = cast(IteratorRelatedEvent, reference_event)
        if strictness >= EventVerificationStrictness.STRICT:
            if not match_optional_maybe_weak_objects(
                self.iterator, reference_event.iterator,
                allow_none=(strictness <= EventVerificationStrictness.STRICT),
            ):
                raise ValueError(
                     'Different iterator objects:'
                    f' expected {reference_event.iterator!r}, got {self.iterator!r}'
                )
    def __repr__(self) -> str:
        if type(self) is IteratorRelatedEvent:  #pylint: disable=unidiomatic-typecheck
            return f'{type(self).__name__}({self.iterator!r})'
        return super().__repr__()
    def __str__(self) -> str:
        return f'event related to the iterator {self.iterator!r}'

class IteratorAdvancedEvent(IteratorRelatedEvent[T]):
    def __init__(self, iterator: OptionalMaybeWeak[Iterator[T]], value: T):
        super().__init__(iterator)
        self.value: T = value
    def verify(
        self,
        reference_event: 'AbstractEvent',
        *, strictness: EventVerificationStrictness = (
            IteratorRelatedEvent._EVENT_VERIFICATION_STRICTNESS_DEFAULT #pylint: disable=protected-access
        ),
    ) -> None:
        super().verify(reference_event, strictness=strictness)
        reference_event = cast(IteratorAdvancedEvent, reference_event)
        if not (eq if MATCH_OBJECTS_USE_EQ_DEFAULT else is_)(self.value, reference_event.value):
            raise ValueError(
                f'Wrong value yielded: expected {reference_event.value!r}, got {self.value!r}'
            )
    def __repr__(self) -> str:
        if type(self) is IteratorAdvancedEvent:  #pylint: disable=unidiomatic-typecheck
            return f'{type(self).__name__}({self.iterator!r}, {self.value!r})'
        return super().__repr__()
    def __str__(self) -> str:
        return f'iterator {self.iterator!r} advanced, extracted value {self.value!r}'

class IteratorExhaustedEvent(IteratorRelatedEvent[T]):
    def __init__(
        self,
        iterator: OptionalMaybeWeak[Iterator[T]],
        exception: Optional[StopIteration] = None,
    ):
        super().__init__(iterator)
        self.exception: Optional[StopIteration] = exception
    def verify(
        self,
        reference_event: 'AbstractEvent',
        *, strictness: EventVerificationStrictness = (
            IteratorRelatedEvent._EVENT_VERIFICATION_STRICTNESS_DEFAULT  #pylint: disable=protected-access
        ),
    ) -> None:
        super().verify(reference_event, strictness=strictness)
        reference_event = cast(IteratorExhaustedEvent, reference_event)
        if strictness >= EventVerificationStrictness.STRICT:
            if not match_optional_objects(
                self.iterator, reference_event.iterator,
                allow_none=(strictness <= EventVerificationStrictness.STRICT),
            ):
                raise ValueError(
                     'Different exception objects:'
                    f' expected {reference_event.exception!r}, got {self.exception!r}'
                )
    def __repr__(self) -> str:
        if type(self) is IteratorExhaustedEvent:    #pylint: disable=unidiomatic-typecheck
            return f'{type(self).__name__}({self.iterator!r})'
        return super().__repr__()
    def __str__(self) -> str:
        return f'iterator {self.iterator!r} exhausted'
