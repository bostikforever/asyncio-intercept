import mapped_deque
import collections
import pytest


def make_std_deque(iterable, maxlen):
    iterable = [] if iterable is None else iterable
    return collections.deque(iterable, maxlen)


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
def test_no_mapping(starting_iterable, maxlen):
    # getitem's
    def _test_get_items():
        m_deque = mapped_deque.MappedDeque(starting_iterable, maxlen)
        deque = make_std_deque(starting_iterable, maxlen)
        assert len(m_deque) == len(deque)
        for i in range(len(m_deque)):
            assert m_deque[i] == deque[i]

    _test_get_items()

    # pop's
    def _test_pops():
        m_deque = mapped_deque.MappedDeque(starting_iterable, maxlen)
        deque = make_std_deque(starting_iterable, maxlen)
        for _ in range(len(m_deque)):
            assert m_deque.pop() == deque.pop()
            assert m_deque == deque

    _test_pops()

    # popleft's
    def _test_poplefts():
        m_deque = mapped_deque.MappedDeque(starting_iterable, maxlen)
        deque = make_std_deque(starting_iterable, maxlen)
        for _ in range(len(m_deque)):
            assert m_deque.popleft() == deque.popleft()
            assert m_deque == deque

    _test_poplefts()


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
def test_func_mapping(starting_iterable, maxlen):
    mapping_func = lambda x: x**2
    # getitem's
    def _test_get_items():
        m_deque = mapped_deque.MappedDeque(starting_iterable, maxlen, mapping_func)
        deque = make_std_deque(starting_iterable, maxlen)
        assert len(m_deque) == len(deque)
        for i in range(len(m_deque)):
            assert m_deque[i] == mapping_func(deque[i])

    _test_get_items()

    # pop's
    def _test_pops():
        m_deque = mapped_deque.MappedDeque(starting_iterable, maxlen, mapping_func)
        deque = make_std_deque(starting_iterable, maxlen)
        for _ in range(len(m_deque)):
            assert m_deque.pop() == mapping_func(deque.pop())
            assert m_deque == deque

    _test_pops()

    # popleft's
    def _test_poplefts():
        m_deque = mapped_deque.MappedDeque(starting_iterable, maxlen, mapping_func)
        deque = make_std_deque(starting_iterable, maxlen)
        for _ in range(len(m_deque)):
            assert m_deque.popleft() == mapping_func(deque.popleft())
            assert m_deque == deque

    _test_poplefts()


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
def test_constructor_mapping(starting_iterable, maxlen):
    class SomeClass:
        def __init__(self, x):
            self._x = x

        def __eq__(self, other: "SomeClass"):
            return self._x == other._x

    # getitem's
    def _test_get_items():
        m_deque = mapped_deque.MappedDeque(starting_iterable, maxlen, SomeClass)
        deque = make_std_deque(starting_iterable, maxlen)
        assert len(m_deque) == len(deque)
        for i in range(len(m_deque)):
            assert m_deque[i] == SomeClass(deque[i])

    _test_get_items()

    # pop's
    def _test_pops():
        m_deque = mapped_deque.MappedDeque(starting_iterable, maxlen, SomeClass)
        deque = make_std_deque(starting_iterable, maxlen)
        for _ in range(len(m_deque)):
            assert m_deque.pop() == SomeClass(deque.pop())
            assert m_deque == deque

    _test_pops()

    # popleft's
    def _test_poplefts():
        m_deque = mapped_deque.MappedDeque(starting_iterable, maxlen, SomeClass)
        deque = make_std_deque(starting_iterable, maxlen)
        for _ in range(len(m_deque)):
            assert m_deque.popleft() == SomeClass(deque.popleft())
            assert m_deque == deque

    _test_poplefts()
