import os
import struct
from typing import Dict, Tuple


class RecorderError(BaseException):
    pass


class IndexBlock:
    """IStream3 index entry"""
    def __init__(self, fd):
        self._block = fd.read(77)
        if len(self._block) != 77:
            raise EOFError()
        self.entry_size,\
            self.block_type,\
            self.stream_type,\
            self.stream_id,\
            self.flags,\
            self.duration,\
            self.timestamp,\
            self.ts_rel,\
            self.dts_rel,\
            self.block_size,\
            self.offset,\
            self.index,\
            self.block_id,\
            self.mark = struct.unpack('=BBBQQQQIIQQQQH', self._block)
        if self.mark != 0xbabe:
            raise EOFError

    @property
    def relative_timestamp(self):
        """returns block relative timestamp in data file"""
        return self.ts_rel

    def __len__(self):
        return self.block_size

    def __repr__(self):
        return f"blk_type={self.block_type} stream_type={self.stream_type} " \
               f"stream_id={self.stream_id} flags={hex(self.flags)} duration={self.duration} " \
               f"timestamp={self.timestamp} ts={self.ts_rel} dts={self.dts_rel} blk size={self.block_size} " \
               f"off={self.offset} idx={self.index} blk_id={self.block_id}"


class Channel:
    def __init__(self, folder) -> None:
        if not os.path.isdir(folder) or not os.path.isfile(os.path.join(folder, 'channel.config')):
            raise RecorderError('invalid channel structure')

        data_file = os.path.join(folder, sorted([fn for fn in os.listdir(folder) if fn.endswith('.data')])[0])
        try:
            index_file = data_file + '.idx'
            self.sps: bytes = b''
            self.pps: bytes = b''
            with open(index_file, 'rb') as idx:
                while True:
                    block: IndexBlock = IndexBlock(idx)
                    if block.block_type == 7:
                        with open(data_file, 'rb') as df:
                            df.seek(block.offset - block.block_size)
                            self.sps = df.read(block.block_size)
                    elif block.block_type == 8:
                        with open(data_file, 'rb') as df:
                            df.seek(block.offset - block.block_size)
                            self.pps = df.read(block.block_size)
                    if self.sps and self.pps:
                        break
        except EOFError:
            raise RecorderError('failed to find sps/pps')


class Recorder:
    def __init__(self):
        root: str = os.getenv('RECORD_ROOT', '')
        self.channels: Dict[str, Channel] = dict()
        self.names = [fn for fn in os.listdir(root) if self._filter_channels(fn, os.path.join(root, fn))]

    def parameters(self, name) -> Tuple[bytes, bytes]:
        c = self.channels.get(name, None)
        return c.sps, c.pps if c else None

    def _filter_channels(self, channel: str, folder: str) -> bool:
        try:
            self.channels[channel] = Channel(folder)
        except (RecorderError, FileNotFoundError, IndexError, EOFError):
            return False
        return True
