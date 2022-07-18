from typing import List
from .atom import FullBox


class SyncSampleBox(FullBox):
    def __init__(self) -> None:
        super().__init__('stss', 0, 0)
        self._entries: List[int] = []
        self._size += 4
        self._frame_number: int = 1

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [super().__bytes__(), len(self._entries).to_bytes(4, 'big')]
        rc.extend([e.to_bytes(4, 'big') for e in self._entries])
        return b''.join(rc)

    def add(self, frame_header: int):
        if frame_header & 0x1f == 5:
            self._entries.append(self._frame_number)
            self._size += 4
        self._frame_number += 1
