import unittest
from geniza.access import Access


class TestAccess(unittest.TestCase):

    def setUp(self):
        key = '123'
        secret_key = 'xyz'
        self.access = Access(key, secret_key)

    def test_hmac(self):
        hmac = self.access.hmac('Ask not for whom the bell tolls')
        expected_hex = '63a73c45f3908562051eb74fbbc9b90f97fab8a6f64748b4e1e5f7f38a0eff79'
        self.assertEqual(expected_hex, hmac)
