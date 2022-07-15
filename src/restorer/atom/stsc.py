from typing import List, Tuple
from .atom import FullBox


class SampleToChunkBox(FullBox):
    def __init__(self) -> None:
        super().__init__('stsc', 0, 0)
        self._entries: List[Tuple[int, int, int]] = []
        self._first_chunk: int = 1
        self._size += 4

    def add(self, frame_size: int):
        if not self._entries:
            self._entries.append((self._first_chunk, 1, 1))
            self._size += 12
        self._first_chunk += 1

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.append(len(self._entries).to_bytes(4, 'big'))
        rc.extend([e.to_bytes(4, 'big') for entry in self._entries for e in entry])
        return b''.join(rc)
