import io
import struct
from typing import List
from .atom.atom import Box
from .atom.stsd import SampleTableBox


def file_size(fl) -> int:
    fl.seek(0, io.SEEK_END)
    rc = fl.tell()
    fl.seek(0, io.SEEK_SET)
    return rc


def is_mdat(b: bytes) -> bool:
    try:
        return b.decode('utf8') == 'mdat'
    except UnicodeDecodeError:
        pass
    return False


def find_mdat(fl) -> int:
    pos: int = fl.tell()
    while True:
        if is_mdat(fl.read(4)):
            return pos
        pos += 1
        fl.seek(pos, io.SEEK_SET)


def read_mdat_size(fl) -> int:
    fl.seek(-8, io.SEEK_CUR)
    size: int = int.from_bytes(fl.read(4), byteorder='big')
    fl.seek(4, io.SEEK_CUR)
    if size == 1:
        size = int.from_bytes(fl.read(8), byteorder='big')
    return size


class InvalidError(BaseException):
    pass


class InvalidIterator:
    def __init__(self, file):
        self._file = file
        self._file_size: int = file_size(file)
        self._position: int = find_mdat(file)
        read_mdat_size(file)

    def __next__(self):
        try:
            frame_size: int = int.from_bytes(self._file.read(4), byteorder='big')
            if not frame_size:
                raise StopIteration
            if self._file.tell() + frame_size <= self._file_size:
                return self._file.read(frame_size)
        except OSError as err:
            print(err)
        raise StopIteration

    def __iter__(self):
        return self


class Invalid:
    def __init__(self, name: str) -> None:
        try:
            self._file = open(name, 'rb')
        except OSError as err:
            raise InvalidError(f'{name} error: {err}')
        self._size = file_size(self._file)
        if self._verify():
            raise InvalidError(f'{name} is valid')
        self._file.seek(0)

    def __len__(self):
        return self._size

    def __del__(self):
        self._file.close()

    def __iter__(self):
        return InvalidIterator(self._file)

    def _verify(self) -> bool:
        atoms: List[str] = []
        while True:
            try:
                pos: int = self._file.tell()
                b = Box(file=self._file)
                atoms.append(str(b))
                if str(b) == 'stsd':
                    stsd: SampleTableBox = SampleTableBox()
                    stsd.parse(self._file)
                pos += 8 if b.container() else len(b)
                if len(b) == 0 or pos == self._size:
                    break
                self._file.seek(pos)
            except struct.error:
                return False
        return 'moov' in atoms
