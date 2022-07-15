from typing import List
from .atom import Box


class FileTypeBox(Box):
    def __init__(self, major_brand: str = 'isom', minor_version: int = 512, compatible_brands: set = None):
        super().__init__('ftyp')
        self._major_brand = major_brand
        self._minor_version = minor_version
        self._compatible_brands = compatible_brands
        if not self._compatible_brands:
            self._compatible_brands = {'isom', 'iso2', 'avc1', 'mp41'}
        self._size += 8 + 4 * len(self._compatible_brands)

    def __bytes__(self) -> bytes:
        rc: List[bytes] = list()
        rc.append(super().__bytes__())
        rc.append(self._major_brand.encode())
        rc.append(self._minor_version.to_bytes(4, 'big'))
        rc.append(''.join(x for x in self._compatible_brands).encode())
        return b''.join(rc)
