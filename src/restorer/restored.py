import argparse
from .atom.mdat import MediaData
from .atom.ftyp import FileTypeBox
from .atom.atom import Container
from .atom.mvhd import MovieHeaderBox
from .atom.tkhd import TrackHeaderBox
from .atom.mdhd import MediaHeaderBox
from .atom.hdlr import HandlerBox
from .atom.vmhd import VideoMediaHeaderBox
from .atom.dref import DataReferenceBox, DataEntryUrlBox
from .atom.stts import TimeToSampleBox
from .atom.stsd import SampleTableBox, VisualSampleEntry
from .atom.stsc import SampleToChunkBox
from .atom.stss import SyncSampleBox
from .atom.stsz import SampleSizeBox
from .atom.stco import ChunkOffsetBox
from .atom.avcc import AvcC
from .invalid import Invalid, InvalidError
from .recorder import Channel, RecorderError


class RestoredError(BaseException):
    pass


class Restored:
    def __init__(self, name: str, **kwargs):
        self._name: str = name
        self._sps: bytes = b''
        self._pps: bytes = b''
        if kwargs.get('channel'):
            channel = Channel(kwargs.get('channel'))
            self._sps = channel.sps
            self._pps = channel.pps
        else:
            if kwargs.get('sps'):
                with open(kwargs.get('sps'), 'rb') as f:
                    self._sps = f.read()
            if kwargs.get('pps'):
                with open(kwargs.get('pps'), 'rb') as f:
                    self._pps = f.read()
        if not self._sps or not self._pps:
            raise RestoredError('sps/pps are required for restoring')
        self._file = None
        self._moov: Container = Container('moov')
        self._moov.add(MovieHeaderBox())
        self._trak: Container = Container('trak')
        self._trak.add(TrackHeaderBox(0, 3, 1, 0, 0, 0))
        self._mdia: Container = Container('mdia')
        self._mdia.add(MediaHeaderBox())
        self._mdia.add(HandlerBox())
        self._minf: Container = Container('minf')
        self._minf.add(VideoMediaHeaderBox())
        dinf: Container = Container('dinf')
        dref: DataReferenceBox = DataReferenceBox()
        dref.add(DataEntryUrlBox(1))
        dinf.add(dref)
        self._minf.add(dinf)
        self._stbl: Container = Container('stbl')
        stsd: SampleTableBox = SampleTableBox()
        stsd.add(VisualSampleEntry('avc1', '', AvcC(self._sps, self._pps)))
        self._stbl.add(stsd)
        self._stts: TimeToSampleBox = TimeToSampleBox()
        self._stsc: SampleToChunkBox = SampleToChunkBox()
        self._stss: SyncSampleBox = SyncSampleBox()
        self._stsz: SampleSizeBox = SampleSizeBox()
        self._stco: ChunkOffsetBox = ChunkOffsetBox()
        self._mdat: MediaData = MediaData()

    def __enter__(self):
        try:
            self._file = open(self._name, 'wb')
        except OSError as err:
            raise RestoredError(err)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stbl.add(self._stts)
        self._stbl.add(self._stss)
        self._stbl.add(self._stsc)
        self._stbl.add(self._stsz)
        self._stbl.add(self._stco)
        self._minf.add(self._stbl)
        self._mdia.add(self._minf)
        self._trak.add(self._mdia)
        self._moov.add(self._trak)
        self._stco.move(len(FileTypeBox()) + len(self._moov) + len(bytes(self._mdat)))
        self._file.write(bytes(FileTypeBox()))
        self._file.write(bytes(self._moov))
        self._file.write(bytes(self._mdat))
        self._file.close()

    def add_frame(self, frame: bytes, ts_delta: int):
        self._stts.add(ts_delta)
        self._stss.add(frame[0])
        self._stsc.add(len(frame))
        self._stco.add(len(frame) + 4)
        self._stsz.add(len(frame) + 4)
        self._mdat.inc(len(frame) + 4)


def restore():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='mp4 format restorer')
    parser.add_argument('invalid', type=str, help='invalid mp4 file')
    parser.add_argument('-channel', type=str, help='invalidly dumped channel')
    parser.add_argument('-sps', type=str, help='stream SPS')
    parser.add_argument('-pps', type=str, help='stream PPS')
    parser.add_argument('restored', type=str, help='restored mp4 file')
    args: argparse.Namespace = parser.parse_args()
    try:
        inv: Invalid = Invalid(args.invalid)
        count: int = 0
        with Restored(args.restored, channel=args.channel, sps=args.sps, pps=args.pps) as r:
            print('reading mdat')
            for frame, percent in inv:
                r.add_frame(frame, 40)
                count += 1
                print(f'frame: {int(count)} ({percent}%)\r', end='')
            print('\ncompiling moov')
        with open(args.restored, 'ab') as f:
            print('storing mdat ')
            count = 0
            for frame, percent in inv:
                f.write(len(frame).to_bytes(4, 'big') + frame)
                count += 1
                print(f'frame: {int(count)} ({percent}%)\r', end='')
        print('\nOk')

    except (InvalidError, RecorderError, FileNotFoundError, IndexError, EOFError) as e:
        print(e)
