from typing import List
from .atom import Box


class AvcC(Box):
    def __init__(self, sps: bytes, pps: bytes) -> None:
        super().__init__(type='avcC')
        self._sps: bytes = sps
        self._pps: bytes = pps
        self._size += 11 + len(self._sps) + len(self._pps)

    def parse(self, file) -> None:
        super()._parse(file)
        file.read(6)
        count: int = int.from_bytes(file.read(2), 'big')
        self._sps = file.read(count)
        file.read(1)
        count: int = int.from_bytes(file.read(2), 'big')
        self._pps = file.read(count)

    @property
    def sps(self) -> bytes:
        return self._sps

    @property
    def pps(self) -> bytes:
        return self._pps

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [
            super().__bytes__(),
            b'\x01', self._sps[1:4], b'\xff',
            b'\xe1', len(self._sps).to_bytes(2, 'big'), self._sps,
            b'\x01', len(self._pps).to_bytes(2, 'big'), self._pps
        ]
        return b''.join(rc)
