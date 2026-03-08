import unittest
from unittest.mock import patch
import api.kroger_auth as kroger_auth

class TestKrogerAuth(unittest.TestCase):
    def test_init_kroger_env(self):
        with patch('os.getenv') as mock_getenv:
            mock_getenv.return_value = 'KROGER_CLIENT_ID'
            kroger_auth.init_kroger_env()
            self.assertTrue(kroger_auth._ENV_LOADED)

if __name__ == '__main__':
    unittest.main()