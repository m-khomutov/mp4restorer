from typing import List, Tuple
from .atom import FullBox


class TimeToSampleBox(FullBox):
    def __init__(self) -> None:
        super().__init__('stts', 0, 0)
        self._entries: List[Tuple[int, int]] = []
        self._size += 4

    def add(self, delta: int):
        if not self._entries or self._entries[-1][1] != delta:
            self._entries.append((1, delta))
            self._size += 8
        else:
            self._entries[-1] = (self._entries[-1][0] + 1, delta)

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [super().__bytes__(), len(self._entries).to_bytes(4, 'big')]
        rc.extend([e.to_bytes(4, 'big') for entry in self._entries for e in entry])
        return b''.join(rc)
