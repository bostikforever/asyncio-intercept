import intercepted_deque
import collections
import pytest
import time


def make_std_deque(iterable, maxlen):
    iterable = [] if iterable is None else iterable
    return collections.deque(iterable, maxlen)


def test_no_interceptor_is_error():
    with pytest.raises(
        AssertionError,
        match="At least one of 'push_interceptor' or 'pop_interceptor' must be specified",
    ):
        intercepted_deque.InterceptedDeque()


class _Intercept:
    def __init__(self):
        self.last_call = time.monotonic_ns()

    def __call__(self):
        self.last_call = time.monotonic_ns()


@pytest.mark.parametrize(
    "push_intercept",
    [
        None,
        _Intercept(),
    ],
)
@pytest.mark.parametrize(
    "pop_intercept",
    [
        None,
        _Intercept(),
    ],
)
@pytest.mark.parametrize(
    "starting_iterable,maxlen",
    (
        (None, None),
        ([], None),
        ([], 1),
        ([1, 2, 3, 4, 5], None),
        ([1, 2, 3, 4, 5], 3),
    ),
)
def test_no_mapping(starting_iterable, maxlen, push_intercept, pop_intercept):
    if push_intercept is None and pop_intercept is None:
        return
    # pop's
    def _test_pops():
        m_deque = intercepted_deque.InterceptedDeque(
            starting_iterable,
            maxlen,
            push_interceptor=push_intercept,
            pop_interceptor=pop_intercept,
        )
        deque = make_std_deque(starting_iterable, maxlen)
        last_intercept_call = None
        for _ in range(len(m_deque)):
            assert m_deque.pop() == deque.pop()
            assert m_deque == deque
            if pop_intercept is not None:
                assert (
                    last_intercept_call is None
                    or last_intercept_call < pop_intercept.last_call
                )
                last_intercept_call = pop_intercept.last_call

    _test_pops()

    # popleft's
    def _test_poplefts():
        m_deque = intercepted_deque.InterceptedDeque(
            starting_iterable,
            maxlen,
            push_interceptor=push_intercept,
            pop_interceptor=pop_intercept,
        )
        deque = make_std_deque(starting_iterable, maxlen)
        for _ in range(len(m_deque)):
            assert m_deque.popleft() == deque.popleft()
            assert m_deque == deque

    _test_poplefts()
