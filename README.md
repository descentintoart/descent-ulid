# descent-ulid

A small, dependency-free ULID generator for Python.

- 48-bit millisecond timestamp plus 80 random bits, Crockford base32
- Monotonic: IDs made in the same millisecond still sort in order
- Safe across threads, and safe if the clock steps backwards

## Install

```text
pip install "descent-ulid @ git+https://github.com/[your-username]/descent-ulid@v0.1.0"
```

## Use

```python
from ulidlib import new_ulid, is_valid, timestamp_of

uid = new_ulid()          # '01JBX...'
is_valid(uid)             # True
timestamp_of(uid)         # datetime in UTC
```

The package installs as `descent-ulid` and imports as `ulidlib`.

## License

MIT