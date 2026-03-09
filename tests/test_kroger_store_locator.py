"""
Unit tests for the kroger_store_locator module.
"""

import unittest
from unittest.mock import patch
from api import kroger_store_locator


class TestKrogerStoreLocator(unittest.TestCase):
    """Test cases for the KrogerStoreLocator class."""

    def test_wrong_init_input(self):
        """Test wrong zip_code input in initialization"""
        zip_code = '123456'

        with self.assertRaises(ValueError):
            kroger_store_locator.KrogerStoreLocator(zip_code)

    @patch("api.kroger_store_locator.init_kroger_env")
    @patch("api.kroger_store_locator.KrogerAPI")
    def test_right_init_input(self, mock_kroger_api, mock_init_env):
        """Test proper KrogerStoreLocator initialization"""

        mock_init_env.return_value = None

        mock_api_instance = mock_kroger_api.return_value
        mock_api_instance.location.search_locations.return_value = {
            "data": [
                {
                    "locationId": "store_1",
                    "chain": "Kroger",
                    "name": "Kroger Totem Lake",
                    "address": {
                        "addressLine1": "12500 120th Ave NE",
                        "city": "Kirkland",
                        "state": "WA"
                    }
                },
                {
                    "locationId": "store_2",
                    "chain": "Kroger",
                    "name": "Kroger Downtown",
                    "address": {
                        "addressLine1": "123 Main St",
                        "city": "Seattle",
                        "state": "WA"
                    }
                },
                {
                    "locationId": "store_3",
                    "chain": "Kroger",
                    "name": "Kroger Bellevue",
                    "address": {
                        "addressLine1": "456 Bellevue Way",
                        "city": "Bellevue",
                        "state": "WA"
                    }
                },
                {
                    "locationId": "store_4",
                    "chain": "Kroger",
                    "name": "Kroger Redmond",
                    "address": {
                        "addressLine1": "789 Redmond Rd",
                        "city": "Redmond",
                        "state": "WA"
                    }
                },
                {
                    "locationId": "store_5",
                    "chain": "Kroger",
                    "name": "Kroger Woodinville",
                    "address": {
                        "addressLine1": "321 Wine Country Rd",
                        "city": "Woodinville",
                        "state": "WA"
                    }
                },
            ]
        }

        locator = kroger_store_locator.KrogerStoreLocator("98034")
        stores = locator.get_stores()

        self.assertEqual(5, len(stores))

    @patch("api.kroger_store_locator.init_kroger_env")
    @patch("api.kroger_store_locator.KrogerAPI")
    def test_get_stores(self, mock_kroger_api, mock_init_env):
        """Test that get_stores returns properly formatted store data."""
        mock_init_env.return_value = None

        mock_api_instance = mock_kroger_api.return_value
        mock_api_instance.location.search_locations.return_value = {
            "data": [
                {
                    "locationId": "store_1",
                    "chain": "Kroger",
                    "name": "Kroger Downtown",
                    "address": {
                        "addressLine1": "123 Main St",
                        "city": "Columbus",
                        "state": "OH",
                    },
                },
                {
                    "locationId": "store_2",
                    "chain": "Kroger",
                    "name": "Kroger East",
                    "address": {
                        "addressLine1": "456 Elm St",
                        "city": "Columbus",
                        "state": "OH",
                    },
                },
            ]
        }

        locator = kroger_store_locator.KrogerStoreLocator("43085")

        result = locator.get_stores()

        self.assertEqual(len(result), 2)

        store = result[0]
        self.assertIn("location_id", store)
        self.assertIn("chain", store)
        self.assertIn("name", store)
        self.assertIn("address", store)

        self.assertEqual(store["location_id"], "store_1")
        self.assertEqual(store["chain"], "Kroger")
        self.assertEqual(store["name"], "Kroger Downtown")
        self.assertEqual(store["address"], "123 Main St, Columbus, OH")


if __name__ == "__main__":
    unittest.main()
