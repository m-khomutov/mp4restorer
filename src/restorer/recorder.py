import json
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
            raise EOFError()

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
            raise RecorderError(f'{folder}: invalid channel structure')

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
            raise RecorderError(f'{folder}: failed to find sps/pps')


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


class Dump:
    _jobs_info_dir_key: str = 'jobs-info-dir'
    _root_dir: str = 'root-dir'

    def __init__(self, conf: str, dump_path: str):
        self._jobs_dir: str = ''
        self._root: str = ''
        self._read_conf(conf)
        if not self._jobs_dir:
            raise RecorderError(f'failed to find key {self.__class__._jobs_info_dir_key} in {conf}')
        if not self._root:
            raise RecorderError(f'failed to find key {self.__class__._root_dir} in {conf}')
        self._channel_path: str = os.path.join(self._root, self._find_channel_path(dump_path))

    @property
    def channel(self):
        return Channel(self._channel_path)

    def _read_conf(self, filename: str):
        with open(filename, 'r') as f:
            in_dumping: bool = False
            for line in f:
                line = line.strip(' ",\n').split(':')
                if len(line) == 2:
                    key = line[0].strip(' ",\n')
                    if key == 'Dumping':
                        in_dumping = True
                    elif in_dumping and key == self.__class__._jobs_info_dir_key:
                        self._jobs_dir = line[1].split('#')[0].strip(' ",\n')
                    elif key == self.__class__._root_dir:
                        self._root = line[1].strip(' [",]\n') if ']' in line[1] else f.readline().strip(' ",\n')
                elif line[0] == '}' and in_dumping:
                    in_dumping = False
                if self._jobs_dir and self._root:
                    break

    def _find_channel_path(self, dump_path: str) -> str:
        for fn in os.listdir(self._jobs_dir):
            with open(os.path.join(self._jobs_dir, fn), 'r') as f:
                job: dict = json.load(f)
                if job['file']['path'] == dump_path:
                    return job['settings']['channelid']
        raise RecorderError(f'failed to find job for dump {dump_path}')
