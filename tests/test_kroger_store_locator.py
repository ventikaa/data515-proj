import unittest
from unittest.mock import patch
from api.kroger_store_locator import KrogerStoreLocator

class TestKrogerStoreLocator(unittest.TestCase):
    @patch('api.kroger_store_locator.init_kroger_env')  # Mock auth
    @patch('api.kroger_store_locator.KrogerAPI')        # Mock API
    def test_get_stores(self, MockKrogerAPI, mock_init_env):
        # Mock init_kroger_env to do nothing
        mock_init_env.return_value = None

        # Set up mock API response with multiple stores
        mock_api_instance = MockKrogerAPI.return_value
        mock_api_instance.location.search_locations.return_value = {
            'data': [
                {
                    "locationId": "store_1",
                    "chain": "Kroger",
                    "name": "Kroger Downtown",
                    "address": {
                        "addressLine1": "123 Main St",
                        "city": "Columbus",
                        "state": "OH"
                    }
                },
                {
                    "locationId": "store_2",
                    "chain": "Kroger",
                    "name": "Kroger East",
                    "address": {
                        "addressLine1": "456 Elm St",
                        "city": "Columbus",
                        "state": "OH"
                    }
                }
            ]
        }

        # Instantiate locator with any zip code (mocked)
        locator = KrogerStoreLocator('43085')

        # Call get_stores
        result = locator.get_stores()

        # Check that we have 2 stores
        self.assertEqual(len(result), 2)

        # Check the structure of the first store
        store = result[0]
        self.assertIn('location_id', store)
        self.assertIn('chain', store)
        self.assertIn('name', store)
        self.assertIn('address', store)

        # Optional: check values match the mocked data
        self.assertEqual(store['location_id'], "store_1")
        self.assertEqual(store['chain'], "Kroger")
        self.assertEqual(store['name'], "Kroger Downtown")
        self.assertEqual(store['address'], "123 Main St, Columbus, OH")

if __name__ == '__main__':
    unittest.main()