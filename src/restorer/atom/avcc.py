from typing import List
from .atom import Box


class AvcC(Box):
    def __init__(self, sps: bytes, pps: bytes):
        super().__init__('avcC')
        self._sps: bytes = sps
        self._pps: bytes = pps
        self._size += 11 + len(self._sps) + len(self._pps)

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.append(b'\x01')
        rc.append(self._sps[1:4])
        rc.append(b'\xff')
        rc.append(b'\xe1')
        rc.append(len(self._sps).to_bytes(2, 'big'))
        rc.append(self._sps)
        rc.append(b'\x01')
        rc.append(len(self._pps).to_bytes(2, 'big'))
        rc.append(self._pps)
        return b''.join(rc)
