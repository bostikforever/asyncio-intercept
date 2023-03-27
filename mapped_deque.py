import collections
import typing

_X = typing.TypeVar("_X")
_T = typing.TypeVar("_T")


class MappedDeque(collections.deque):
    def __init__(
        self,
        iterable: typing.Optional[typing.Iterable[_T]] = None,
        maxlen: typing.Optional[int] = None,
        mapping: typing.Optional[typing.Callable[[_T], _X]] = None,
    ):
        iterable = [] if iterable is None else iterable
        super().__init__(iterable, maxlen)
        self._mapping = mapping
        if self._mapping is None:
            self._get_item = super().__getitem__
            self.pop = super().pop
            self.popleft = super().popleft

    def pop(self) -> _X:
        return self._mapping(super().pop())

    def popleft(self) -> _X:
        return self._mapping(super().popleft())

    # These methods of deque don't take slices, unlike MutableSequence, hence the type: ignores
    def __getitem__(self, __index: typing.SupportsIndex) -> _X:
        return self._get_item(__index)

    def _get_item(self, __index: typing.SupportsIndex) -> _X:
        return self._mapping(super().__getitem__(__index))
