from typing import List
from .atom import FullBox


class VideoMediaHeaderBox(FullBox):
    def __init__(self) -> None:
        super().__init__('vmhd', 0, 1)
        self._size += 8

    def __bytes__(self) -> bytes:
        return b''.join([super().__bytes__(), b'\x00\x00\x00\x00\x00\x00\x00\x00'])
