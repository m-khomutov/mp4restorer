from .atom import Box


class MediaData(Box):
    def __init__(self):
        super().__init__('mdat')

    def inc(self, value: int):
        self._size += value
