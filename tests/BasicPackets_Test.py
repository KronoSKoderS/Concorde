import unittest

from random import randint

from calpack import models


class TestSimplePackets(unittest.TestCase):
    def setUp(self):
        class simple_pkt(models.Packet):
            field1 = models.IntField()
            field2 = models.IntField()
            field3 = models.IntField(num_words=10)

        self.simple_pkt = simple_pkt

    def test_set_simple_int_fields(self):
        p = self.simple_pkt()

        v1 = randint(0,100)
        v2 = randint(0,100)

        p.field1 = v1
        p.field2 = v2

        self.assertEqual(p.field1, v1)
        self.assertEqual(p.field2, v2)

    def test_set_invalid_int_field(self):
        p = self.simple_pkt()
        
        with self.assertRaises(TypeError):
            p.field1 = ""

    def test_set_array_field(self):
        p = self.simple_pkt()

        t_array = [randint(0,100) for i in range(10)]

        p.field3 = t_array
        self.assertEqual(p.field3, t_array)

## TDD: Prototyping for encapsulated packets.
# class TestAdvancedPackets(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def test_encapsulated_pkt(self):
#         class simple_pkt(models.Packet):
#             field1 = models.IntField(num_words=10)
#
#         class adv_pkt(models.Packet):
#             field2 = simple_pkt
#
#         p = adv_pkt()
#
#         # Verify abilily to access and set encap packets fields
#         p.field2.field1 = 100
#
#         self.assertEquals(p.field2.field1, 100)
#
#         sp = simple_pkt()
#         sp.field1 = 200
#
#         p.field2 = sp
#
#         self.assertEquals(p.field2.field1, 200)


if __name__ == '__main__':
    unittest.main()
