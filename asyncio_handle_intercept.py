import asyncio
import typing

AsyncIOHandle = typing.Union[asyncio.Handle, asyncio.TimerHandle]
RunFunction = typing.Callable[[], None]


class _Handle(asyncio.Handle):
    __slots__ = ("__base", "_run")

    def __init__(self, base: asyncio.Handle, run: RunFunction):
        self.__base = base
        self._run = run

    def __getattr__(self, item):
        return getattr(self.__base, item)


class _TimerHandle(asyncio.TimerHandle):
    __slots__ = ("__base", "_run")

    def __init__(self, base: asyncio.TimerHandle, run: RunFunction):
        self.__base = base
        self._run = run

    def __getattr__(self, item):
        return getattr(self.__base, item)


def _make_wrapped_handle(handle: AsyncIOHandle, run: RunFunction):
    if isinstance(handle, asyncio.Handle):
        return _Handle(handle, run)
    if isinstance(handle, asyncio.TimerHandle):
        return _TimerHandle(handle, run)
    assert False


class HandleInterceptor:
    def __init__(
        self,
        *,
        # TODO: consider the implication of the intercepting functions raising
        pre_run: typing.Optional[RunFunction] = None,
        post_run: typing.Optional[RunFunction] = None
    ):
        assert (
            pre_run is not None or post_run is not None
        ), "At least one of 'pre_run' or 'post_run' must be specified"
        self._pre_run = pre_run
        self._post_run = post_run

    # TODO: typing should make it obvious that the interceptor does not change the type
    # of the handle (i.e no transition from asyncio.Handle to asyncio.TimerHandle and
    # vice-versa)
    def intercept_handle(self, handle: AsyncIOHandle) -> AsyncIOHandle:
        _old_run = handle._run
        intercepted_run = self._make_intercepted_run(_old_run)
        intercepted_handle = _make_wrapped_handle(handle, intercepted_run)
        return intercepted_handle

    def _make_intercepted_run(self, run_func: RunFunction):
        def intercepted_run_both():
            try:
                self._pre_run()
            except:
                run_func()
            else:
                try:
                    run_func()
                finally:
                    try:
                        self._post_run()
                    except:
                        ...

        def intercepted_run_pre():
            try:
                self._pre_run()
            except:
                ...
            run_func()

        def intercepted_run_post():
            try:
                run_func()
            finally:
                try:
                    self._post_run()
                except:
                    ...

        if self._pre_run is not None and self._post_run is not None:
            return intercepted_run_both
        if self._pre_run is not None:
            return intercepted_run_pre
        if self._post_run is not None:
            return intercepted_run_post
        assert False
