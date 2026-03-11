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

    def test_init_kroger_env_failure(self):
        """Checking if .env file doesn't have the credentials needed for Kroger API"""
        kroger_auth.ENV_LOADED = False

        with patch("api.kroger_auth.load_and_validate_env") as mock_validate:
            mock_validate.side_effect = Exception("Missing credentials")

            with self.assertRaises(Exception):
                kroger_auth.init_kroger_env()

if __name__ == "__main__":
    unittest.main()
