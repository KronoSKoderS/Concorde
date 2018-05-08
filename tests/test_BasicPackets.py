import unittest
import ctypes
import struct
import sys

from calpack import models
from calpack.utils import PYPY


class Test_BasicPacket(unittest.TestCase):

    def test_pkt_create_packet_object_with_defined_values(self):
        class two_int_field_packet(models.Packet):
            int_field = models.IntField()
            int_field_signed = models.IntField(signed=True)

        p = two_int_field_packet(int_field=12, int_field_signed=-12)
        self.assertEqual(p.int_field, 12)
        self.assertEqual(p.int_field_signed, -12)

    def test_pkt_create_packet_with_default_field_value(self):
        class two_int_field_packet(models.Packet):
            int_field = models.IntField(default_val=12)
            int_field_signed = models.IntField(signed=True, default_val=-12)

        p = two_int_field_packet()
        self.assertEqual(p.int_field, 12)
        self.assertEqual(p.int_field_signed, -12)

    def test_pkt_create_class_from_bytes_string(self):
        """
        This test verifies that a class can be created from a byte string and
        that the values are properly parsed.
        """

        class two_int_field_packet(models.Packet):
            int_field = models.IntField()
            int_field_signed = models.IntField(signed=True)

        class c_two_int_field_packet(ctypes.Structure):
            _fields_ = (
                ('int_field', ctypes.c_uint),
                ('int_field_signed', ctypes.c_int)
            )

        val_1 = 34
        val_2 = -12

        c_pkt = c_two_int_field_packet()
        c_pkt.int_field = val_1
        c_pkt.int_field_signed = val_2

        b_val = ctypes.string_at(ctypes.addressof(c_pkt), ctypes.sizeof(c_two_int_field_packet))

        pkt = two_int_field_packet.from_bytes(b_val)

        self.assertEqual(pkt.int_field, val_1)
        self.assertEqual(pkt._Packet__c_pkt.int_field, val_1)
        self.assertEqual(pkt.int_field_signed, val_2)
        self.assertEqual(pkt._Packet__c_pkt.int_field_signed, val_2)

    def test_pkt_compare_two_same_packets(self):
        class two_int_field_packet(models.Packet):
            int_field = models.IntField()
            int_field_signed = models.IntField(signed=True)

        pkt1 = two_int_field_packet(int_field=1, int_field_signed=-1)
        pkt2 = two_int_field_packet(int_field=1, int_field_signed=-1)

        self.assertEqual(pkt1, pkt2)

    def test_pkt_compare_two_different_packets(self):

        class two_int_field_packet(models.Packet):
            int_field = models.IntField()
            int_field_signed = models.IntField(signed=True)

        class two_int_field_packet_2(models.Packet):
            int_field = models.IntField()
            int_field_signed = models.IntField(signed=True)

        pkt_orig = two_int_field_packet(int_field=1, int_field_signed=-1)
        pkt_different_class_same_byte_out = two_int_field_packet_2(
            int_field=1,
            int_field_signed=-1
        )

        # even though these packets will generate the same byte output and the
        # fields are the same, this should raise an error as their classes are
        # not the same.
        self.assertFalse(pkt_orig == pkt_different_class_same_byte_out)

        class three_int_field_packet(models.Packet):
            int_field = models.IntField()
            int_field_2 = models.IntField()
            int_field_3 = models.IntField()

        pkt_different_class_different_byte_out = three_int_field_packet(
            int_field=1,
            int_field_2=2,
            int_field_3=3
        )
        self.assertFalse(pkt_orig == pkt_different_class_different_byte_out)

        pkt_same_class_different_values = two_int_field_packet(
            int_field=1,
            int_field_signed=2
        )
        self.assertFalse(pkt_orig == pkt_same_class_different_values)

    def test_pkt_export_to_bytes_string(self):
        class two_int_field_packet(models.Packet):
            int_field = models.IntField()
            int_field_signed = models.IntField(signed=True)

        class c_two_int_field_packet(ctypes.Structure):
            _fields_ = (
                ('int_field', ctypes.c_uint),
                ('int_field_signed', ctypes.c_int),
            )

        val_1 = 54
        val_2 = -23

        c_pkt = c_two_int_field_packet()
        c_pkt.int_field = val_1
        c_pkt.int_field_signed = val_2

        b_val = ctypes.string_at(ctypes.addressof(c_pkt), ctypes.sizeof(c_two_int_field_packet))

        pkt = two_int_field_packet()
        pkt.int_field = val_1
        pkt.int_field_signed = val_2

        pkt_bin = pkt.to_bytes()

        self.assertEqual(pkt_bin, b_val)

    def test_pkt_to_bytes_string_then_import_from_binary(self):
        class two_int_field_packet(models.Packet):
            int_field = models.IntField()
            int_field_signed = models.IntField(signed=True)

        val_1 = 96
        val_2 = -3

        p = two_int_field_packet()
        p.int_field = val_1
        p.int_field_signed = val_2

        p2 = two_int_field_packet.from_bytes(p.to_bytes())

        self.assertEqual(p.int_field, p2.int_field)
        self.assertEqual(p.int_field_signed, p2.int_field_signed)

    def test_pkt_two_instances_different_field_instances(self):
        class simple_pkt(models.Packet):
            int_field = models.IntField()
            int_field_signed = models.IntField(signed=True)

        p1 = simple_pkt()
        p2 = simple_pkt()

        p1.int_field = 1
        p2.int_field = 2

        p1.int_field_signed = -1
        p2.int_field_signed = -2

        self.assertFalse(p1 is p2)
        self.assertFalse(p1.int_field is p2.int_field)

        self.assertNotEqual(p1.int_field, p2.int_field)
        self.assertNotEqual(p1.int_field_signed, p2.int_field_signed)

    def test_pkt_len(self):
        class simple_pkt(models.Packet):
            int_field = models.IntField()
            int_field_signed = models.IntField(signed=True)

        class c_simple_pkt(ctypes.Structure):
            _fields_ = (
                ('int_field', ctypes.c_uint),
                ('int_field_signed', ctypes.c_int)
            )

        p1 = simple_pkt()

        self.assertEqual(len(p1), ctypes.sizeof(c_simple_pkt))


class Test_EndianPacket(unittest.TestCase):

    def test_little_endian_packet_from_bytes(self):

        # As of 22 Feb '18, PyPy does not support non-native endianess
        if PYPY:
            return True

        class little_packet(models.PacketLittleEndian):
            field1 = models.IntField()
            field2 = models.IntField()

        b_val = struct.pack("<II", 0xdeadbeef, 0xbeefcafe)

        pkt = little_packet.from_bytes(b_val)

        self.assertEqual(pkt.field1, 0xdeadbeef)
        self.assertEqual(pkt.field2, 0xbeefcafe)


    def test_little_endian_packet_to_bytes(self):

        # As of 22 Feb '18, PyPy does not support non-native endianess
        if PYPY:
            return True

        class little_packet(models.PacketLittleEndian):
            field1 = models.IntField()
            field2 = models.IntField()

        expected_b_val = struct.pack("<II", 0xdeadbeef, 0xbeefcafe)

        pkt = little_packet(
            field1 = 0xdeadbeef,
            field2 = 0xbeefcafe
        )

        self.assertEqual(pkt.to_bytes(), expected_b_val)


    def test_big_endian_packet_from_bytes(self):

        # As of 22 Feb '18, PyPy does not support non-native endianess
        if PYPY:
            return True

        class big_packet(models.PacketBigEndian):
            field1 = models.IntField()
            field2 = models.IntField()

        b_val = struct.pack(">II", 0xdeadbeef, 0xbeefcafe)

        pkt = big_packet.from_bytes(b_val)

        self.assertEqual(pkt.field1, 0xdeadbeef)
        self.assertEqual(pkt.field2, 0xbeefcafe)


    def test_big_endian_packet_to_bytes(self):

        # As of 22 Feb '18, PyPy does not support non-native endianess
        if PYPY:
            return True

        class big_packet(models.PacketBigEndian):
            field1 = models.IntField()
            field2 = models.IntField()

        expected_b_val = struct.pack(">II", 0xdeadbeef, 0xbeefcafe)

        pkt = big_packet(
            field1 = 0xdeadbeef,
            field2 = 0xbeefcafe
        )

        self.assertEqual(pkt.to_bytes(), expected_b_val)

if __name__ == '__main__':
    unittest.main()
