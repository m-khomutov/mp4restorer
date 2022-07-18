import time
from typing import List
from .atom import FullBox


class TrackHeaderBox(FullBox):
    def __init__(self, version: int = 0, flags: int = 0,
                 track_id: int = 1, duration: int = 0, width: int = 0, height: int = 0) -> None:
        super().__init__('tkhd', version, flags)
        self._track_id: int = track_id
        self._duration: int = duration
        self._width: int = width
        self._height: int = height
        sz: int = 8 if self._version else 4
        self._size += 3 * sz + 8 + 60

    def __bytes__(self) -> bytes:
        sz: int = 8 if self._version else 4
        rc: List[bytes] = [
            super().__bytes__(),
            int(time.time()).to_bytes(sz, 'big'),
            int(time.time()).to_bytes(sz, 'big'),
            self._track_id.to_bytes(4, 'big'),
            b'\x00\x00\x00\x00',
            self._duration.to_bytes(sz, 'big')
        ]
        rc.extend([b'\x00' for _ in range(16)])
        rc.extend([x.to_bytes(4, 'big') for x in [0x00010000, 0, 0, 0, 0x00010000, 0, 0, 0, 0x40000000]])
        rc.append(self._width.to_bytes(4, 'big'))
        rc.append(self._height.to_bytes(4, 'big'))
        return b''.join(rc)
