import time
from typing import List
from .atom import FullBox


class Language:
    def __init__(self, value: str):
        self._value, off = 0, 14
        for s in value:
            d = ord(s)-0x60
            for i in range(5):
                self._value |= ((d >> i) & 1) << off
                off -= 1

    def __bytes__(self) -> bytes:
        return self._value.to_bytes(2, 'big')


class MediaHeaderBox(FullBox):
    def __init__(self, version: int = 0, timescale: int = 1000, duration: int = 0, lang: str = 'und') -> None:
        super().__init__('mdhd', version, 0)
        self._timescale: int = timescale
        self._duration: int = duration
        self._language: Language = Language(lang)
        sz: int = 8 if self._version else 4
        self._size += 3 * sz + 8

    def __bytes__(self) -> bytes:
        sz: int = 8 if self._version else 4
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.append(int(time.time()).to_bytes(sz, 'big'))
        rc.append(int(time.time()).to_bytes(sz, 'big'))
        rc.append(self._timescale.to_bytes(4, 'big'))
        rc.append(self._duration.to_bytes(sz, 'big'))
        rc.append(bytes(self._language))
        rc.append(b'\x00\x00')
        return b''.join(rc)
