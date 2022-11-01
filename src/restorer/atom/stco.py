from typing import List, Union
from .atom import FullBox


class ChunkOffsetBox(FullBox):
    def __init__(self, co64: Union[bool, None]) -> None:
        self._offset_size = 8 if co64 is not None and co64 is True else 4
        super().__init__('stco' if self._offset_size == 4 else 'co64', 0, 0)
        self._entries: List[int] = []
        self._size += 4
        self._current_offset: int = 0

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [super().__bytes__(), len(self._entries).to_bytes(4, 'big')]
        rc.extend([e.to_bytes(self._offset_size, 'big') for e in self._entries])
        return b''.join(rc)

    def add(self, frame: bytes):
        if frame[0] & 0x1f == 5:
            self._entries.append(self._current_offset)
            self._size += self._offset_size
        self._current_offset += len(frame) + 4

    def move(self, offset: int):
        for i, _ in enumerate(self._entries):
            self._entries[i] += offset
