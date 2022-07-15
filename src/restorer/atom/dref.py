from typing import List
from .atom import FullBox


class DataEntryUrlBox(FullBox):
    def __init__(self, flags_: int, location: str = '') -> None:
        super().__init__('url ', 0, flags_)
        self._location: str = location
        self._size += len(self._location)

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.append(self._location.encode())
        return b''.join(rc)


class DataEntryUrnBox(FullBox):
    def __init__(self, flags_: int, name: str = '', location: str = '') -> None:
        super().__init__('urn ', 0, flags_)
        self._name: str = name
        self._location: str = location
        self._size += len(self._name) + len(self._location) + 1

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.append(self._name.encode())
        rc.append(b'\x00')
        rc.append(self._location.encode())
        return b''.join(rc)


class DataReferenceBox(FullBox):
    def __init__(self) -> None:
        super().__init__('dref', 0, 0)
        self._entries: List[FullBox] = []
        self._size += 4

    def add(self, box: FullBox):
        self._entries.append(box)
        self._size += len(box)

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.append(len(self._entries).to_bytes(4, 'big'))
        if self._entries:
            rc.extend([bytes(x) for x in self._entries])
        return b''.join(rc)
