from collections.abc import Callable
from typing import TypeAlias, TypeVar
from weakref import ReferenceType

T = TypeVar('T')

WeakRefCallback: TypeAlias = Callable[[ReferenceType[T]], None]

MaybeWeak: TypeAlias = T | ReferenceType[T]
