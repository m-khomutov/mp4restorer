from typing import List
from .atom import FullBox


class VideoMediaHeaderBox(FullBox):
    def __init__(self) -> None:
        super().__init__('vmhd', 0, 1)
        self._size += 8

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.extend([b'\x00' for _ in range(8)])
        return b''.join(rc)
