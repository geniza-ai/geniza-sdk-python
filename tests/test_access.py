import unittest
from geniza_sdk_python.access import Access


class TestAccess(unittest.TestCase):

    def setUp(self):
        key = '123'
        secret_key = 'xyz'
        self.access = Access(key, secret_key)

    def testHmac(self):
        hmac = self.access.hmac('Ask not for whom the bell tolls')
        expected_hex = '63A73C45F3908562051EB74FBBC9B90F97FAB8A6F64748B4E1E5F7F38A0EFF79'
        self.assertEqual(expected_hex, hmac)
