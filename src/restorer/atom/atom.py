from typing import List


class Box:
    def __init__(self, type_: str, extended_type: bytes = bytes()) -> None:
        self._size: int = 8
        self._type: str = type_
        self._extended_type: bytes = extended_type

    def __bytes__(self) -> bytes:
        rc: List[bytes] = []
        if self._size <= 0xfffffffe:
            rc.append(self._size.to_bytes(4, 'big'))
        else:
            rc.append(int(1).to_bytes(4, 'big'))
        rc.append(self._type.encode())
        if self._size > 0xfffffffe:
            rc.append((self._size + 8).to_bytes(8, 'big'))
        rc.append(self._extended_type)
        return b''.join(rc)

    def __len__(self) -> int:
        return self._size

    def __repr__(self):
        return f'{self.__class__.__name__}(type={self._type})'


class FullBox(Box):
    def __init__(self, type_: str, version_: int, flags_: int) -> None:
        super().__init__(type_)
        self._version: int = version_
        self._flags: int = flags_
        self._size += 4

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.append(self._version.to_bytes(1, 'big'))
        rc.append(self._flags.to_bytes(3, 'big'))
        return b''.join(rc)


class Container(Box):
    def __init__(self, type_: str) -> None:
        super().__init__(type_)
        self._contained: List[Box] = []

    def add(self, box: Box) -> None:
        self._contained.append(box)
        self._size += len(box)

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.extend([bytes(x) for x in self._contained])
        return b''.join(rc)
