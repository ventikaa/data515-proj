"""
Unit tests for the kroger_auth module.
"""

import unittest
from unittest.mock import patch
from api import kroger_auth


class TestKrogerAuth(unittest.TestCase):
    """Test cases for the kroger_auth module."""

    def test_init_kroger_env(self):
        """Test that init_kroger_env sets the environment loaded flag."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "KROGER_CLIENT_ID"
            kroger_auth.init_kroger_env()
            self.assertTrue(kroger_auth.ENV_LOADED)


if __name__ == "__main__":
    unittest.main()
