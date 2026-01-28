from collections.abc import Callable
from typing import Generic, NamedTuple, Optional, TypeAlias, TypeVar
from weakref import ReferenceType, ref

from testing_events_tracking._events import OptionalMaybeWeak


T = TypeVar('T')


WeakRefCallback: TypeAlias = Callable[[ReferenceType[T]], None]

MaybeWeak: TypeAlias = T | ReferenceType[T]


def make_maybe_weak(
    obj: T, *, weak: bool = True, weak_callback: Optional[WeakRefCallback[T]] = None,
) -> MaybeWeak[T]:
    if weak:
        ref_args_extra = []
        if weak_callback is not None:
            ref_args_extra.append(weak_callback)
        return ref(obj, *ref_args_extra)
    return obj


class RecordMaybeWeakObjectOptions(NamedTuple, Generic[T]):
    weak: bool
    weak_callback: Optional[WeakRefCallback[T]] = None


class RecordingObjectConverter(Generic[T]):

    def __init__(self, options: Optional[RecordMaybeWeakObjectOptions[T]] = None):
        self._options = options

    def __call__(self, obj: T) -> OptionalMaybeWeak[T]:
        if self._options is None:
            return None
        return make_maybe_weak(
            obj,
            weak=self._options.weak,
            weak_callback=self._options.weak_callback,
        )
