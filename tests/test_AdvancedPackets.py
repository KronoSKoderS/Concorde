from calpack import models
import unittest
import ctypes


class Test_AdvancedPacket(unittest.TestCase):

    def test_advpkt_enc_array_pkts(self):
        class Point(models.Packet):
            x = models.IntField()
            y = models.IntField()

        class EncArray(models.Packet):
            points = models.ArrayField(
                models.PacketField(Point),
                10
            )

        pkt = EncArray()

        for i, point in enumerate(pkt.points):
            point.x = 100
            point.y = 50

            self.assertEqual(pkt.points[i].x, 100)
            self.assertEqual(pkt._Packet__c_pkt.points[i].x, 100)

            self.assertEqual(pkt.points[i].y, 50)
            self.assertEqual(pkt._Packet__c_pkt.points[i].y, 50)

    def test_advpkt_inception_enc_pkt(self):
        class Point(models.Packet):
            x = models.IntField()
            y = models.IntField()

        class TenPoints(models.Packet):
            points = models.ArrayField(
                models.PacketField(Point),
                8
            )

        class TwoTenPoints(models.Packet):
            points_one = models.PacketField(TenPoints)
            points_two = models.PacketField(TenPoints)

        pkt = TwoTenPoints()

        for i, point in enumerate(pkt.points_one.points):
            point.x = 100
            point.y = 50

            self.assertEqual(pkt.points_one.points[i].x, 100)
            self.assertEqual(pkt._Packet__c_pkt.points_one.points[i].x, 100)

            self.assertEqual(pkt.points_one.points[i].y, 50)
            self.assertEqual(pkt._Packet__c_pkt.points_one.points[i].y, 50)

        for i, point in enumerate(pkt.points_two.points):
            point.x = 100
            point.y = 50

            self.assertEqual(pkt.points_two.points[i].x, 100)
            self.assertEqual(pkt._Packet__c_pkt.points_two.points[i].x, 100)

            self.assertEqual(pkt.points_two.points[i].y, 50)
            self.assertEqual(pkt._Packet__c_pkt.points_two.points[i].y, 50)

    def test_advpkt_verify_AttributeError_invalid_field_name_set_c_field(self):
        class Point(models.Packet):
            x = models.IntField()
            y = models.IntField()

        p = Point()
        with self.assertRaises(AttributeError):
            p.set_c_field('bad_name', 100)

    def test_advpkt_create_complex_packet(self):
        """
        This test creates a packet that contains all the known built-in fields and ensures that
        the packet is correctly created and parsed back in.
        """

        class Point(models.Packet):
            x = models.IntField8()
            y = models.IntField8()

        class PrimaryPacket(models.Packet):
            int_field = models.IntField()
            float_field = models.FloatField()
            double_field = models.DoubleField()
            long_double_field = models.LongDoubleField()
            pkt_field = models.PacketField(Point)
            bool_field = models.BoolField()

        class c_Point(ctypes.Structure):
            _fields_ = (
                ('x', ctypes.c_uint8),
                ('y', ctypes.c_uint8)
            )

        class c_PrimaryPacket(ctypes.Structure):
            _fields_ = (
                ('int_field', ctypes.c_uint),
                ('float_field', ctypes.c_float),
                ('double_field', ctypes.c_double),
                ('long_double_field', ctypes.c_longdouble),
                ('pkt_field', c_Point),
                ('bool_field', ctypes.c_bool)
            )

        pkt = PrimaryPacket(
            int_field=3,
            float_field=3.14,
            double_field=-3.14,
            long_double_field=123.456,
            bool_field=True
        )

        c_pkt = c_PrimaryPacket()
        c_pkt.int_field = 3
        c_pkt.float_field = 3.14
        c_pkt.double_field = -3.14
        c_pkt.long_double_field = 123.456
        c_pkt.bool_field = True

        b_str = pkt.to_bytes()
        c_b_str = ctypes.string_at(ctypes.addressof(c_pkt), ctypes.sizeof(c_PrimaryPacket))

        self.assertEqual(b_str, c_b_str)

        parsed_pkt = PrimaryPacket.from_bytes(c_b_str)

        self.assertEqual(parsed_pkt.int_field, 3)
        self.assertAlmostEqual(parsed_pkt.float_field, 3.14, places=5)
        self.assertAlmostEqual(parsed_pkt.double_field, -3.14, places=5)
        self.assertAlmostEqual(parsed_pkt.long_double_field, 123.456, places=5)
        self.assertEqual(parsed_pkt.bool_field, True)

    def test_advpkt_inheritance(self):
        """
        This test verifies the functionality of Class Inheritance for Packets.
        See also GitHub Issue #84 (https://github.com/KronoSKoderS/CalPack/issues/84)
        """

        class TemplatePacket(models.Packet):
            PKT_UID = 0x00

            ID = models.IntField8()
            TYPE = models.IntField8()
            reserved0 = models.IntField16(bit_len=7)
            length = models.IntField16(bit_len=9)
            reserved1 = models.IntField32(bit_len=4)
            utcTimeUpper = models.IntField32(bit_len=28)
            utcTimeLower = models.IntField32()
            PacketStatus = models.IntField32()
            padding = models.IntField32()   
        
        class MyPacket(TemplatePacket): 
            PKT_UID = 0x0E


        t_pkt = TemplatePacket()
        m_pkt = MyPacket()

        # First let's check the original issue of the packet length:
        self.assertEqual(len(t_pkt), len(m_pkt))

        # Next, let's for sure verify that the fields are there:
        self.assertEqual(t_pkt.ID, m_pkt.ID)
        self.assertEqual(t_pkt.length, m_pkt.length)

        # Next, let's verify that the packets are indeed different:
        t_pkt.PacketStatus = 0xbeefcafe
        m_pkt.PacketStatus = 0xdeadbeef
        self.assertNotEqual(t_pkt.PacketStatus, m_pkt.PacketStatus)

        m_pkt.PacketStatus = 0xbeefcafe

        # check to make sure the output of the byte data
        # is the same
        self.assertEqual(t_pkt.to_bytes(), m_pkt.to_bytes())


        # Check to make sure the PKT_UID's remain correct
        self.assertEqual(t_pkt.PKT_UID, 0x00)
        self.assertEqual(m_pkt.PKT_UID, 0x0E)
