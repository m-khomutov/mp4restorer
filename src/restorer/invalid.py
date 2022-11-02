import base64
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
        self._frame: List[bytes] = []
        read_mdat_size(file)

    def __next__(self):
        try:
            while True:
                frame_size: int = int.from_bytes(self._file.read(4), byteorder='big')
                if not frame_size:
                    return self._generate_last_frame()
                if self._file.tell() + frame_size <= self._file_size:
                    rc: bytes = self._generate_frame(self._file.read(frame_size))
                    if rc:
                        return rc
        except OSError as err:
            print(err)
        return self._generate_last_frame()

    def __iter__(self):
        return self

    def _generate_frame(self, slice_: bytes):
        if 1 <= (slice_[0] & 0x1f) <= 5:
            first_mb_in_slice: bool = (slice_[1] >> 7) == 1
            rc: bytes = b''
            if first_mb_in_slice:
                if self._frame:
                    rc = b''.join(self._frame)
                    self._frame = []
            else:
                self._frame.append(b'\x00\x00\x00\x01')
            self._frame.append(slice_)
            return rc
        return slice_

    def _generate_last_frame(self):
        if self._frame:
            rc = b''.join(self._frame)
            self._frame = []
            return rc
        raise StopIteration


class Invalid:
    def __init__(self, name: str, with_verification: bool) -> None:
        try:
            self._file = open(name, 'rb')
        except OSError as err:
            raise InvalidError(f'{name} error: {err}')
        self._size = file_size(self._file)
        if with_verification and self._verify():
            raise InvalidError(f'{name} is valid')
        self._file.seek(0)

    def sprop(self) -> str:
        while True:
            try:
                pos: int = self._file.tell()
                if str(box := Box(file=self._file)) == 'stsd':
                    stsd: SampleTableBox = SampleTableBox()
                    stsd.parse(self._file)
                    for entry in stsd:
                        if str(entry) == 'avc1':
                            return ''.join([base64.b64encode(entry.avcc.sps).decode('utf-8'),
                                            ',',
                                            base64.b64encode(entry.avcc.pps).decode('utf-8')])
                pos += 8 if box.container() else len(box)
                if len(box) == 0 or pos == self._size:
                    break
                self._file.seek(pos)
            except struct.error:
                break
        raise InvalidError('failed to find sps/pps in dump')

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
                box = Box(file=self._file)
                atoms.append(str(box))
                pos += len(box)
                if len(box) == 0 or pos == self._size:
                    break
                self._file.seek(pos)
            except struct.error:
                return False
        return 'moov' in atoms
