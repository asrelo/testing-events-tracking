from enum import IntEnum
from operator import is_, eq
from typing import Any, TypeAlias, Optional, TypeVar, cast
from weakref import ReferenceType

from testing_events_tracking._common.weakref import MaybeWeak

__all__ = (
    'OptionalMaybeWeak',
    'match_objects',
    'match_optional_objects',
    'match_maybe_weak_objects',
    'match_optional_maybe_weak_objects',
    'EventVerificationStrictness',
    'AbstractEvent',
)

T = TypeVar('T')

OptionalMaybeWeak: TypeAlias = Optional[MaybeWeak[T]]

def _from_maybe_weak(obj: MaybeWeak[T]) -> T:
    if isinstance(obj, ReferenceType):
        obj_extracted = cast(T, obj())
        if obj_extracted is None:   # btw None itself cannot be referenced
            raise ReferenceError('weakly referenced object no longer exists')
        obj = obj_extracted
    return obj

def _optional_from_maybe_weak(obj: MaybeWeak[T]) -> Optional[T]:
    try:
        return _from_maybe_weak(obj)
    except ReferenceError:
        return None

MATCH_OBJECTS_USE_EQ_DEFAULT: bool = True
MATCH_OBJECTS_ALLOW_NONE_DEFAULT: bool = False

def match_objects(
    obj1: Any, obj2: Any, /, *, use_eq: bool = MATCH_OBJECTS_USE_EQ_DEFAULT,
) -> bool:
    return (eq if use_eq else is_)(obj1, obj2)

def match_optional_objects(
    obj1: object, obj2: object, /,
    *, use_eq: bool = MATCH_OBJECTS_USE_EQ_DEFAULT,
    allow_none: bool = MATCH_OBJECTS_ALLOW_NONE_DEFAULT,
) -> bool:
    if any((x is None) for x in (obj1, obj2)):
        return allow_none
    return match_maybe_weak_objects(obj1, obj2, use_eq=use_eq)

def match_maybe_weak_objects(
    obj1: MaybeWeak, obj2: MaybeWeak, /,
    *, use_eq: bool = MATCH_OBJECTS_USE_EQ_DEFAULT,
    allow_none: bool = MATCH_OBJECTS_ALLOW_NONE_DEFAULT,
) -> bool:
    obj1 = _optional_from_maybe_weak(obj1)
    obj2 = _optional_from_maybe_weak(obj2)
    if any((x is None) for x in (obj1, obj2)):
        return allow_none
    return match_objects(obj1, obj2, use_eq=use_eq)

def match_optional_maybe_weak_objects(
    obj1: Optional[MaybeWeak], obj2: Optional[MaybeWeak], /,
    *, use_eq: bool = MATCH_OBJECTS_USE_EQ_DEFAULT,
    allow_none: bool = MATCH_OBJECTS_ALLOW_NONE_DEFAULT,
) -> bool:
    if any((x is None) for x in (obj1, obj2)):
        return allow_none
    return match_maybe_weak_objects(obj1, obj2, use_eq=use_eq)

class EventVerificationStrictness(IntEnum):
    LOOSE = 0x0
    STRICT = 0x10
    EXACT = 0x20

# XXX: __repr__ and __str__ methods on events...

class AbstractEvent:
    _EVENT_VERIFICATION_STRICTNESS_DEFAULT: EventVerificationStrictness = (
        EventVerificationStrictness.STRICT
    )
    def _is_event_of_compatible_type(
        self,
        reference_event: 'AbstractEvent',
        *, strictness: EventVerificationStrictness = _EVENT_VERIFICATION_STRICTNESS_DEFAULT,
    ) -> bool:
        _ = strictness
        return isinstance(reference_event, type(self))
    def verify_type(
        self,
        reference_event: 'AbstractEvent',
        *, strictness: EventVerificationStrictness = _EVENT_VERIFICATION_STRICTNESS_DEFAULT,
    ) -> None:
        if not self._is_event_of_compatible_type(reference_event, strictness=strictness):
            raise TypeError(
                f'Wrong type: expected {type(reference_event)!r} ({reference_event!r}),'
                f' got {type(self)!r} ({self!r})'
            )
    def verify(
        self,
        reference_event: 'AbstractEvent',
        *, strictness: EventVerificationStrictness = _EVENT_VERIFICATION_STRICTNESS_DEFAULT,
    ) -> None:
        _ = strictness
        self.verify_type(reference_event, strictness=strictness)
