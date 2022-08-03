from typing import List, Tuple
from .atom import FullBox


class SampleToChunkBox(FullBox):
    def __init__(self) -> None:
        super().__init__('stsc', 0, 0)
        self._entries: List[Tuple[int, int, int]] = []
        self._first_chunk: int = 1
        self._frames_in_chunk: int = 0
        self._size += 4

    def add(self, unit_header: int):
        if unit_header & 0x1f == 5:
            self.flush()
        self._frames_in_chunk += 1

    def flush(self) -> FullBox:
        if self._frames_in_chunk:
            self._entries.append((self._first_chunk, self._frames_in_chunk, 1))
            self._size += 12
            self._first_chunk += 1
            self._frames_in_chunk = 0
        return self

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [super().__bytes__(), len(self._entries).to_bytes(4, 'big')]
        rc.extend([e.to_bytes(4, 'big') for entry in self._entries for e in entry])
        return b''.join(rc)
