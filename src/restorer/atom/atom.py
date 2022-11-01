import struct
from typing import List


class Box:
    def __init__(self, **kwargs) -> None:
        self._size: int = 8
        self._type: str = kwargs.get('type', '    ')
        self._extended_type: bytes = kwargs.get('extended', b'')
        self._parse(kwargs.get('file'))

    def container(self) -> bool:
        ret = (self._type == 'moov' or self._type == 'trak' or self._type == 'edts')
        ret = (ret or self._type == 'mdia' or self._type == 'minf' or self._type == 'dinf')
        ret = (ret or self._type == 'stbl' or self._type == 'mvex' or self._type == 'moof')
        return ret or self._type == 'traf'

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

    def __str__(self):
        return self._type

    def __repr__(self):
        return f'{self.__class__.__name__}(size={self._size} type={self._type})'

    def _parse(self, file):
        if file:
            self._size, t = struct.unpack('!II', file.read(8))
            self._type = ''.join(chr((t >> (i * 8)) & 0xff) for i in range(3, -1, -1))
            if self._size == 1:
                self._size = struct.unpack('!Q', file.read(8))[0]


class FullBox(Box):
    def __init__(self, type_: str, version_: int, flags_: int) -> None:
        super().__init__(type=type_)
        self._version: int = version_
        self._flags: int = flags_
        self._size += 4

    def parse(self, file):
        self._version.from_bytes(file.read(1), 'big')
        self._flags.from_bytes(file.read(3), 'big')

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [
            super().__bytes__(),
            self._version.to_bytes(1, 'big'),
            self._flags.to_bytes(3, 'big'),
        ]
        return b''.join(rc)


class Container(Box):
    def __init__(self, type_: str) -> None:
        super().__init__(type=type_)
        self._contained: List[Box] = []

    def add(self, box: Box) -> None:
        self._contained.append(box)
        self._size += len(box)

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [super().__bytes__()]
        rc.extend([bytes(x) for x in self._contained])
        return b''.join(rc)
