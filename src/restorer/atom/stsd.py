from typing import List
from .atom import Box, FullBox
from .avcc import AvcC


class SampleEntry(Box):
    def __init__(self, type_: str):
        super().__init__(type=type_)
        self._size += 8
        self._ref_index: int = 1

    def parse(self, file):
        file.read(6)
        self._ref_index.from_bytes(file.read(2), 'big')

    def __bytes__(self):
        return b''.join([super().__bytes__(), b'\x00\x00\x00\x00\x00\x00\x00\x01'])


class VisualSampleEntry(SampleEntry):
    def __init__(self, coding_name: str, compressor: str, avcc: AvcC):
        super().__init__(coding_name)
        self._compressor: bytes = compressor[:32].encode()
        if len(self._compressor) < 32:
            self._compressor += bytes([0]*(32-len(self._compressor)))
        self._width: int = 0
        self._height: int = 0
        self._avcc: AvcC = avcc
        self._size += 70 + len(self._avcc)

    def parse(self, file):
        super().parse(file)
        file.read(16)
        self._width.from_bytes(file.read(2), 'big')
        self._height.from_bytes(file.read(2), 'big')
        file.read(14)
        self._compressor = file.read(32).decode()
        file.read(4)
        self._avcc.parse(file)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def avcc(self):
        return self._avcc

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [
            super().__bytes__(),
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            self._width.to_bytes(2, 'big'),
            self._height.to_bytes(2, 'big'),
            b'\x00\x48\x00\x00',
            b'\x00\x48\x00\x00',
            b'\x00\x00\x00\x00',
            b'\x00\x01',
            self._compressor,
            b'\x00\x18',
            b'\xff\xff',
            bytes(self._avcc)
        ]
        return b''.join(rc)


class SampleTableBox(FullBox):
    def __init__(self) -> None:
        super().__init__('stsd', 0, 0)
        self._entries: List[Box] = []
        self._size += 4

    def parse(self, file):
        super().parse(file)
        count: int = int.from_bytes(file.read(4), 'big')
        for _ in range(count):
            b: Box = Box(file=file)
            if str(b) == 'avc1':
                self._entries.append(VisualSampleEntry(str(b), ' '*32, AvcC(b'', b'')))
                self._entries[-1].parse(file)

    def add(self, entry: SampleEntry) -> None:
        self._entries.append(entry)
        self._size += len(entry)

    def __bytes__(self) -> bytes:
        rc: List[bytes] = [super().__bytes__(), len(self._entries).to_bytes(4, 'big')]
        rc.extend([bytes(e) for e in self._entries])
        return b''.join(rc)

    def __iter__(self):
        return (x for x in self._entries)
