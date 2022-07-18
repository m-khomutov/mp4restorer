import time
from typing import List
from .atom import FullBox


class MovieHeaderBox(FullBox):
    def __init__(self, version: int = 0, timescale: int = 1000, duration: int = 0) -> None:
        super().__init__('mvhd', version, 0)
        self._timescale: int = timescale
        self._duration: int = duration
        self._next_track_id = 2
        sz: int = 8 if self._version else 4
        self._size += 3 * sz + 4 + 80

    def __bytes__(self) -> bytes:
        sz: int = 8 if self._version else 4
        rc: List[bytes] = [
            super().__bytes__(),
            int(time.time()).to_bytes(sz, 'big'),
            int(time.time()).to_bytes(sz, 'big'),
            self._timescale.to_bytes(4, 'big'),
            self._duration.to_bytes(sz, 'big'),
            b'\x00\x01\x00\x00',
            b'\x01\x00'
        ]
        rc.extend([b'\x00' for _ in range(10)])
        rc.extend([x.to_bytes(4, 'big') for x in [0x00010000, 0, 0, 0, 0x00010000, 0, 0, 0, 0x40000000]])
        rc.extend([b'\x00' for _ in range(24)])
        rc.append(self._next_track_id.to_bytes(4, 'big'))
        return b''.join(rc)

    def add_track(self) -> None:
        self._next_track_id += 1

    def track_id(self) -> int:
        return self._next_track_id
