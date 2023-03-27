import collections
import typing

_T = typing.TypeVar("_T")


Interceptor = typing.Callable[[], None]


class InterceptedDeque(collections.deque):
    def __init__(
        self,
        iterable: typing.Optional[typing.Iterable[_T]] = None,
        maxlen: typing.Optional[int] = None,
        push_interceptor: typing.Optional[Interceptor] = None,
        pop_interceptor: typing.Optional[Interceptor] = None,
    ):
        iterable = [] if iterable is None else iterable
        super().__init__(iterable, maxlen)
        assert (
            push_interceptor is not None or pop_interceptor is not None
        ), "At least one of 'push_interceptor' or 'pop_interceptor' must be specified"
        self._push_interceptor = push_interceptor
        self._pop_interceptor = pop_interceptor
        if self._pop_interceptor is None:
            self.pop = super().pop
            self.popleft = super().popleft
        if self._push_interceptor is None:
            self.append = super().append
            self.appendleft = super().appendleft

    def pop(self) -> _T:
        ret = super().pop()
        self._pop_interceptor()
        return ret

    def popleft(self) -> _T:
        ret = super().popleft()
        self._pop_interceptor()
        return ret

    def append(self, x: _T):
        self._push_interceptor()
        super().append(x)

    def appendleft(self, x: _T):
        self._push_interceptor()
        super().appendleft(x)
