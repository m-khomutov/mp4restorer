from typing import List
from .atom import FullBox


class HandlerBox(FullBox):
    def __init__(self, handler_: str = 'vide', name: str = 'VideoHandler') -> None:
        super().__init__('hdlr', 0, 0)
        self._handler: str = handler_
        self._name: str = name
        self._size += 21 + len(self._name)

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [
            super().__bytes__(),
            b'\x00\x00\x00\x00',
            self._handler.encode(),
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            self._name.encode(), b'\x00'
        ]
        return b''.join(rc)
