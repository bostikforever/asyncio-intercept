import asyncio
import logging
import timed_event_loop
import time
import pytest


class TimeRecorder(timed_event_loop.AbstractTimeRecorder):
    def __init__(self):
        self._curr_event_start = None
        self.events = []

    def start_event(self):
        assert self._curr_event_start is None
        self._curr_event_start = time.time()

    def end_event(self):
        assert self._curr_event_start is not None
        self.events.append(time.time() - self._curr_event_start)
        logging.info("Event took %s secs", self.events[-1])
        self._curr_event_start = None


async def block_coro(block_duration):
    time.sleep(block_duration)


_STEP = 0.1


@pytest.mark.parametrize("block_duration", [(_STEP * i) for i in range(0, 10)])
def test_timed_event_loop(block_duration):
    test_time_recorder = TimeRecorder()
    timed_event_loop_policy = timed_event_loop.TimedEventLoopPolicy(
        lambda: test_time_recorder
    )
    asyncio.set_event_loop_policy(timed_event_loop_policy)
    asyncio.run(block_coro(block_duration))
    events = test_time_recorder.events
    assert block_duration + _STEP > max(events) >= block_duration
