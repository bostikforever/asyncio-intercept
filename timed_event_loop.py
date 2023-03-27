import asyncio
import asyncio.base_events as aio_base_events
import asyncio_handle_intercept
import typing
import mapped_deque


class AbstractTimeRecorder(typing.Protocol):
    def start_event():
        ...

    def end_event():
        ...


class TimedEventLoop(asyncio.DefaultEventLoopPolicy._loop_factory):
    def __init__(self, time_recorder: AbstractTimeRecorder):
        super().__init__()
        handle_interceptor = asyncio_handle_intercept.HandleInterceptor(
            pre_run=time_recorder.start_event, post_run=time_recorder.end_event
        )
        self._ready = mapped_deque.MappedDeque(
            mapping=handle_interceptor.intercept_handle
        )


class TimedEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    def __init__(
        self, time_recorder_factory: typing.Callable[[], AbstractTimeRecorder]
    ):
        super().__init__()
        self._time_recorder_factory = time_recorder_factory

    def new_event_loop(self) -> asyncio.AbstractEventLoop:
        return TimedEventLoop(self._time_recorder_factory())
