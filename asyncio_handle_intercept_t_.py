import asyncio_handle_intercept as intercept
import asyncio
import time
import typing
import pytest
import logging


def test_no_interceptor_is_error():
    with pytest.raises(
        AssertionError,
        match="At least one of 'pre_run' or 'post_run' must be specified",
    ):
        intercept.HandleInterceptor()


class HandleFactory(typing.Protocol):
    def __call__(
        self, *args, **kwargs
    ) -> typing.Union[asyncio.Handle, asyncio.TimerHandle]:
        pass


def _handle_test_common(handle_factory: HandleFactory):
    def test_pre_run():
        pre_run_ns = None
        run_ns = None

        def pre_run_func():
            nonlocal pre_run_ns
            pre_run_ns = time.monotonic_ns()

        def run_func():
            nonlocal run_ns
            run_ns = time.monotonic_ns()

        # No args to run_func
        handle = handle_factory(run_func, [], asyncio.get_running_loop())
        handle_interceptor = intercept.HandleInterceptor(pre_run=pre_run_func)
        intercepted_handle = handle_interceptor.intercept_handle(handle)
        intercepted_handle._run()
        assert pre_run_ns is not None
        assert run_ns is not None
        assert pre_run_ns < run_ns

    test_pre_run()

    def test_post_run():
        run_ns = None
        post_run_ns = None

        def run_func():
            nonlocal run_ns
            run_ns = time.monotonic_ns()

        def post_run_func():
            nonlocal post_run_ns
            post_run_ns = time.monotonic_ns()

        # No args to run_func
        handle = handle_factory(run_func, [], asyncio.get_running_loop())
        handle_interceptor = intercept.HandleInterceptor(post_run=post_run_func)
        intercepted_handle = handle_interceptor.intercept_handle(handle)
        intercepted_handle._run()
        assert run_ns is not None
        assert post_run_ns is not None
        assert run_ns < post_run_ns

    test_post_run()

    def test_pre_and_post_run():
        pre_run_ns = None
        run_ns = None
        post_run_ns = None

        def pre_run_func():
            nonlocal pre_run_ns
            pre_run_ns = time.monotonic_ns()

        def run_func():
            nonlocal run_ns
            run_ns = time.monotonic_ns()

        def post_run_func():
            nonlocal post_run_ns
            post_run_ns = time.monotonic_ns()

        # No args to run_func
        handle = handle_factory(run_func, [], asyncio.get_running_loop())
        handle_interceptor = intercept.HandleInterceptor(
            pre_run=pre_run_func, post_run=post_run_func
        )
        intercepted_handle = handle_interceptor.intercept_handle(handle)
        intercepted_handle._run()
        assert pre_run_ns is not None
        assert run_ns is not None
        assert post_run_ns is not None
        assert pre_run_ns < run_ns < post_run_ns

    test_pre_and_post_run()


def _create_intercepted(
    handle_factory: HandleFactory,
    run_func: intercept.RunFunction,
    pre_run_func: intercept.RunFunction,
    post_run_func: intercept.RunFunction,
):
    handle = handle_factory(run_func, [], asyncio.get_running_loop())
    handle_interceptor = intercept.HandleInterceptor(
        pre_run=pre_run_func, post_run=post_run_func
    )
    intercepted_handle = handle_interceptor.intercept_handle(handle)
    return intercepted_handle


def _handle_perf_test_creation(handle_factory: HandleFactory):
    def pre_run_func():
        pre_run_ns = time.monotonic_ns()

    def run_func():
        run_ns = time.monotonic_ns()

    def post_run_func():
        post_run_ns = time.monotonic_ns()

    ROUNDS = 100_000
    start_plain = time.perf_counter()
    for _ in range(ROUNDS):
        handle_factory(run_func, [], asyncio.get_running_loop())

    logging.info(
        "Time running %s rounds of plain constructor: %s (s)",
        ROUNDS,
        time.perf_counter() - start_plain,
    )

    start_intercepted = time.perf_counter()
    for _ in range(ROUNDS):
        _create_intercepted(handle_factory, run_func, pre_run_func, post_run_func)

    logging.info(
        "Time running %s rounds of intercepted construction: %s (s)",
        ROUNDS,
        time.perf_counter() - start_intercepted,
    )


def _handle_perf_test_call_run(handle_factory: HandleFactory):
    def pre_run_func():
        pre_run_ns = time.monotonic_ns()

    def run_func():
        run_ns = time.monotonic_ns()

    def post_run_func():
        post_run_ns = time.monotonic_ns()

    ROUNDS = 100_000
    plain_handle = handle_factory(run_func, [], asyncio.get_running_loop())
    start_plain = time.perf_counter()
    for _ in range(ROUNDS):
        plain_handle._run()

    logging.info(
        "Time running %s rounds of plain _run: %s (s)",
        ROUNDS,
        time.perf_counter() - start_plain,
    )

    intercepted_handle = _create_intercepted(
        handle_factory, run_func, pre_run_func, post_run_func
    )
    start_intercepted = time.perf_counter()
    for _ in range(ROUNDS):
        intercepted_handle._run()

    logging.info(
        "Time running %s rounds of intercepted _run: %s (s)",
        ROUNDS,
        time.perf_counter() - start_intercepted,
    )


@pytest.mark.asyncio
async def test_asyncio_handle():
    _handle_test_common(asyncio.Handle)
    _handle_perf_test_creation(asyncio.Handle)
    _handle_perf_test_call_run(asyncio.Handle)


@pytest.mark.asyncio
async def test_asyncio_timer_handle():
    # We use when = 0, because we do not run these via the event loop so we don't
    # really care about the timing functionality.
    timer_handle_factory = lambda *args, **kwargs: asyncio.TimerHandle(
        0, *args, **kwargs
    )
    _handle_test_common(timer_handle_factory)
    _handle_perf_test_creation(timer_handle_factory)
    _handle_perf_test_call_run(timer_handle_factory)
