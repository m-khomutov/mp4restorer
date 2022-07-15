import unittest
from restorer.atom.atom import Box, FullBox, Container


class BoxTest(unittest.TestCase):
    def testNormalCaseWorks(self):
        self.assertEqual(
            bytes(Box('free')),
            b'\x00\x00\x00\x08\x66\x72\x65\x65')

    def testHugeBoxCaseWorks(self):
        class HugeBox(Box):
            def __init__(self):
                super().__init__('huge')
                self._size += 0x0100000000

        self.assertEqual(
            bytes(HugeBox()),
            b'\x00\x00\x00\x01\x68\x75\x67\x65\x00\x00\x00\x01\x00\x00\x00\x10')


class FullBoxTest(unittest.TestCase):
    def testNormalCaseWorks(self):
        self.assertEqual(
            bytes(FullBox('tkhd', 0, 3)),
            b'\x00\x00\x00\x0c\x74\x6b\x68\x64\x00\x00\x00\x03')


class ContainerTest(unittest.TestCase):
    def testNormalCaseWorks(self):
        moov: Container = Container('moov')
        moov.add(FullBox('mvhd', 0, 0))
        self.assertEqual(
            bytes(moov),
            b'\x00\x00\x00\x14\x6d\x6f\x6f\x76\x00\x00\x00\x0c\x6d\x76\x68\x64\x00\x00\x00\x00')


if __name__ == '__main__':
    unittest.main()
