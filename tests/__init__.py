import unittest
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

def get_tests():
    return full_suite()


def full_suite():

    from tests.IntField_Test import Test_IntField
    from tests.BasicPackets_Test import Test_BasicPacket
    from tests.ArrayField_Test import Test_ArrayField
    from tests.PacketField_Test import Test_PacketField
    from tests.Utilities_Test import Test_Utilities
    from tests.AdvancedPackets_Test import Test_AdvancedPacket
    from tests.FlagField_Test import Test_FlagField
    from tests.FloatFields_Test import Test_FloatField, Test_DoubleField, Test_LongDoubleField

    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(Test_BasicPacket),
        unittest.TestLoader().loadTestsFromTestCase(Test_IntField),
        unittest.TestLoader().loadTestsFromTestCase(Test_ArrayField),
        unittest.TestLoader().loadTestsFromTestCase(Test_PacketField),
        unittest.TestLoader().loadTestsFromTestCase(Test_Utilities),
        unittest.TestLoader().loadTestsFromTestCase(Test_AdvancedPacket),
        unittest.TestLoader().loadTestsFromTestCase(Test_FlagField),
        unittest.TestLoader().loadTestsFromTestCase(Test_FloatField),
        unittest.TestLoader().loadTestsFromTestCase(Test_DoubleField),
        unittest.TestLoader().loadTestsFromTestCase(Test_LongDoubleField),
    ])

if __name__ == "__main__":
    unittest.main()
