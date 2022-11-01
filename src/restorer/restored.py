import argparse
import base64

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
from .recorder import Channel, RecorderError, Dump


class RestoredError(BaseException):
    pass


class Restored:
    def __init__(self, name: str, **kwargs):
        self._name: str = name
        self._sps: bytes = b''
        self._pps: bytes = b''
        channel: Channel = kwargs.get('channel')
        if channel:
            self._sps = channel.sps
            self._pps = channel.pps
        else:
            if kwargs.get('sps'):
                with open(kwargs.get('sps'), 'rb') as f:
                    self._sps = f.read()
            if kwargs.get('pps'):
                with open(kwargs.get('pps'), 'rb') as f:
                    self._pps = f.read()
            if kwargs.get('sprop'):
                self._parse_sprop(kwargs.get('sprop'))
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
        self._stco: ChunkOffsetBox = ChunkOffsetBox(kwargs.get('co64'))
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
        self._stbl.add(self._stsc.flush())
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
        self._stsc.add(frame[0])
        self._stco.add(frame)
        self._stsz.add(len(frame) + 4)
        self._mdat.inc(len(frame) + 4)

    def _parse_sprop(self, sprop: str):
        ps = sprop.split(',')
        if len(ps) == 2:
            self._sps = base64.b64decode(ps[0])
            self._pps = base64.b64decode(ps[1])


def restore():
    parser = argparse.ArgumentParser(description='Verifies dumped mp4 file. Restores if invalid')
    parser.add_argument('-sps', type=str, help='stream SPS')
    parser.add_argument('-pps', type=str, help='stream PPS')
    parser.add_argument('-sprop', type=str, help='current-sprop-string')
    parser.add_argument('-conf', type=str, help='recorder configuration file')
    parser.add_argument('dump', type=str, help='dumped file to check')
    args: argparse.Namespace = parser.parse_args()
    try:
        inv: Invalid = Invalid(args.dump)
        r_name: str = args.dump.split('.mp4')[0] + '-r.mp4'
        with Restored(r_name,
                      channel=Dump(args.conf, args.dump).channel,
                      sps=args.sps,
                      pps=args.pps,
                      sprop=args.sprop,
                      co64=len(inv) > 0xfffffff0) as r:
            for frame in inv:
                r.add_frame(frame, 40)
        with open(r_name, 'ab') as f:
            for frame in inv:
                f.write(len(frame).to_bytes(4, 'big') + frame)
    except (InvalidError, RecorderError, RestoredError, FileNotFoundError, IndexError, EOFError) as e:
        print(e)
