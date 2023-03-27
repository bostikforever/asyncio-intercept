import asyncio
import contextlib
import typing

AsyncIOHandle = typing.Union[asyncio.Handle, asyncio.TimerHandle]
RunFunction = typing.Callable[[], None]


class _Handle(asyncio.Handle):
    __slots__ = ("__base", "_intercept")

    def __init__(self, base: asyncio.Handle, intercept):
        self.__base = base
        self._intercept = intercept

    def _run(self):
        with self._intercept():
            super()._run()

    def __getattr__(self, item):
        return getattr(self.__base, item)


class _TimerHandle(asyncio.TimerHandle):
    __slots__ = ("__base", "_intercept")

    def __init__(self, base: asyncio.TimerHandle, intercept):
        self.__base = base
        self._intercept = intercept

    def _run(self):
        with self._intercept():
            super()._run()

    def __getattr__(self, item):
        return getattr(self.__base, item)


def _make_wrapped_handle(handle: AsyncIOHandle, intercept):
    if isinstance(handle, asyncio.TimerHandle):
        return _TimerHandle(handle, intercept)
    if isinstance(handle, asyncio.Handle):
        return _Handle(handle, intercept)
    assert False


class HandleInterceptor:
    def __init__(
        self,
        *,
        # TODO: consider changing the API to take a context manager instead, that way
        # we run '_run' in the context of the passed context manager and exception
        # handling is implied
        pre_run: typing.Optional[RunFunction] = None,
        post_run: typing.Optional[RunFunction] = None
    ):
        assert (
            pre_run is not None or post_run is not None
        ), "At least one of pre_run or post_run must be specified"
        self._pre_run = pre_run
        self._post_run = post_run

    # TODO: typing should make it obvious that the interceptor does not change the type
    # of the handle (i.e no transition from asyncio.Handle to asyncio.TimerHandle and
    # vice-versa)
    def intercept_handle(self, handle: AsyncIOHandle) -> AsyncIOHandle:
        intercept = self._make_intercept()
        intercepted_handle = _make_wrapped_handle(handle, intercept)
        return intercepted_handle

    def _make_intercept(self):

        # TODO: consider implications of intercept functions throwing
        if self._pre_run is not None and self._post_run is not None:

            @contextlib.contextmanager
            def intercept():
                try:
                    self._pre_run()
                except:
                    yield
                else:
                    try:
                        yield
                    finally:
                        self._post_run()

            return intercept

        if self._pre_run is not None:

            @contextlib.contextmanager
            def intercept():
                try:
                    self._pre_run()
                except:
                    pass  # TODO: implication of throwing here? See related TODO above
                yield

            return intercept

        if self._post_run is not None:

            @contextlib.contextmanager
            def intercept():
                try:
                    yield
                finally:
                    self._post_run()

            return intercept
        assert False
