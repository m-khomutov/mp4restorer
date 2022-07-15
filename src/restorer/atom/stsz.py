from typing import List
from .atom import FullBox


class SampleSizeBox(FullBox):
    def __init__(self) -> None:
        super().__init__('stsz', 0, 0)
        self._entries: List[int] = []
        self._size += 8

    def add(self, size: int):
        self._entries.append(size)
        self._size += 4

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.append(int(0).to_bytes(4, 'big'))
        rc.append(len(self._entries).to_bytes(4, 'big'))
        rc.extend([sz.to_bytes(4, 'big') for sz in self._entries])
        return b''.join(rc)
