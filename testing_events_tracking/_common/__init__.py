from typing import Optional, TypeVar
from weakref import ref

from .weakref import WeakRefCallback, MaybeWeak

T = TypeVar('T')

def make_maybe_weak(
    obj: T, *, weak: bool = True, weak_callback: Optional[WeakRefCallback[T]] = None,
) -> MaybeWeak[T]:
    if weak:
        ref_args_extra = []
        if weak_callback is not None:
            ref_args_extra.append(weak_callback)
        return ref(obj, *ref_args_extra)
    return obj
