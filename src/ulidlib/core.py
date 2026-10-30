import os
import threading
import time
from datetime import datetime, timezone

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford base32: no I, L, O, U
_DECODE = {c: i for i, c in enumerate(ALPHABET)}

_lock = threading.Lock()
_last_ms = -1
_last_rand = 0


def _encode(value: int, length: int) -> str:
    chars = []
    for _ in range(length):
        chars.append(ALPHABET[value & 31])
        value >>= 5
    return "".join(reversed(chars))


def new_ulid() -> str:
    global _last_ms, _last_rand
    with _lock:
        ms = time.time_ns() // 1_000_000
        if ms <= _last_ms:
            # Same millisecond, or the clock stepped back: add one to stay in order
            ms = _last_ms
            _last_rand += 1
            if _last_rand >= 1 << 80:
                raise OverflowError("ULID random part used up for this millisecond")
        else:
            _last_ms = ms
            _last_rand = int.from_bytes(os.urandom(10), "big")
        return _encode(ms, 10) + _encode(_last_rand, 16)


def is_valid(ulid: str) -> bool:
    if not isinstance(ulid, str) or len(ulid) != 26:
        return False
    ulid = ulid.upper()
    if any(c not in _DECODE for c in ulid):
        return False
    return ulid[0] in "01234567"  # anything higher overflows 128 bits


def timestamp_of(ulid: str) -> datetime:
    if not is_valid(ulid):
        raise ValueError(f"Not a valid ULID: {ulid!r}")
    ms = 0
    for c in ulid[:10].upper():
        ms = ms * 32 + _DECODE[c]
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
