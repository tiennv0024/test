from app.services.playback_service import LOOP_ALL, LOOP_OFF, LOOP_ONE, PlaybackQueue


def test_next_previous_and_loop_off():
    queue = PlaybackQueue([1, 2], loop_mode=LOOP_OFF)

    assert queue.current() == 1
    assert queue.next() == 2
    assert queue.next() is None
    assert queue.previous() == 1


def test_loop_all_wraps():
    queue = PlaybackQueue([1, 2], current_index=1, loop_mode=LOOP_ALL)

    assert queue.next() == 1
    assert queue.previous() == 2


def test_loop_one_replays_current():
    queue = PlaybackQueue([1, 2], loop_mode=LOOP_ONE)

    assert queue.next() == 1


def test_shuffle_retains_same_set_and_current():
    queue = PlaybackQueue([1, 2, 3, 4], current_index=2)
    current = queue.current()

    queue.set_shuffle(True)

    assert set(queue.track_ids) == {1, 2, 3, 4}
    assert queue.current() == current
