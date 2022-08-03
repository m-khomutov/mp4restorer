from typing import List
from .atom import FullBox


class ChunkOffsetBox(FullBox):
    def __init__(self) -> None:
        super().__init__('stco', 0, 0)
        self._entries: List[int] = []
        self._size += 4
        self._current_offset: int = 0

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [super().__bytes__(), len(self._entries).to_bytes(4, 'big')]
        rc.extend([e.to_bytes(4, 'big') for e in self._entries])
        return b''.join(rc)

    def add(self, frame: bytes):
        if frame[0] & 0x1f == 5:
            self._entries.append(self._current_offset)
            self._size += 4
        self._current_offset += len(frame) + 4

    def move(self, offset: int):
        for i, _ in enumerate(self._entries):
            self._entries[i] += offset
