import threading
from datetime import datetime, timedelta, timezone

import pytest

import ulidlib.core as core
from ulidlib import is_valid, new_ulid, timestamp_of


@pytest.fixture(autouse=True)
def reset_generator(monkeypatch):
    """Start every test with a fresh generator, so a faked clock can't leak."""
    monkeypatch.setattr(core, "_last_ms", -1)
    monkeypatch.setattr(core, "_last_rand", 0)


def test_format():
    u = new_ulid()
    assert len(u) == 26
    assert all(c in core.ALPHABET for c in u)
    assert is_valid(u)


def test_ids_sort_in_creation_order():
    ids = [new_ulid() for _ in range(10_000)]
    assert ids == sorted(ids)


def test_ids_are_unique():
    ids = [new_ulid() for _ in range(10_000)]
    assert len(set(ids)) == len(ids)


def test_unique_across_threads():
    results = []
    lock = threading.Lock()

    def worker():
        local = [new_ulid() for _ in range(1_000)]
        with lock:
            results.extend(local)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(set(results)) == 8_000


def test_same_millisecond_increments(monkeypatch):
    monkeypatch.setattr(core.time, "time_ns", lambda: 1_700_000_000_000 * 1_000_000)
    a, b = new_ulid(), new_ulid()
    assert a[:10] == b[:10]
    assert b > a


def test_clock_going_backwards_stays_ordered(monkeypatch):
    now = [1_800_000_000_000 * 1_000_000]
    monkeypatch.setattr(core.time, "time_ns", lambda: now[0])
    a = new_ulid()
    now[0] -= 5_000 * 1_000_000  # clock steps back five seconds
    b = new_ulid()
    assert b > a


def test_timestamp_round_trip():
    before = datetime.now(timezone.utc) - timedelta(milliseconds=1)
    u = new_ulid()
    after = datetime.now(timezone.utc) + timedelta(milliseconds=1)
    assert before <= timestamp_of(u) <= after


def test_lowercase_is_accepted():
    u = new_ulid()
    assert is_valid(u.lower())
    assert timestamp_of(u.lower()) == timestamp_of(u)


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "too-short",
        "0" * 25,
        "0" * 27,
        "0" * 25 + "I",
        "0" * 25 + "L",
        "0" * 25 + "O",
        "0" * 25 + "U",
        "8" + "0" * 25,
        None,
        12345,
    ],
)
def test_invalid_input(bad):
    assert not is_valid(bad)


def test_timestamp_of_rejects_invalid():
    with pytest.raises(ValueError):
        timestamp_of("not-a-ulid")