import unittest
from unittest.mock import patch
from api.kroger_shopping_cart import ShoppingCart

class TestKrogerShoppingCart(unittest.TestCase):
    @patch('api.kroger_shopping_cart.init_kroger_env')  # Mock auth
    @patch('api.kroger_shopping_cart.KrogerAPI')        # Mock API
    def test_price_ingredients(self, MockKrogerAPI, mock_init_env):
        # Mock init_kroger_env to do nothing
        mock_init_env.return_value = None

        # Set up mock API response
        mock_api_instance = MockKrogerAPI.return_value
        mock_api_instance.product.search_products.side_effect = [
            # Response for ingredient1
            {
                'data': [
                    {
                        'description': 'Mock Ingredient 1',
                        'productId': '123',
                        'items': [{'price': {'regular': 1.99}, 'size': '1 unit'}]
                    }
                ]
            },
            # Response for ingredient2
            {
                'data': [
                    {
                        'description': 'Mock Ingredient 2',
                        'productId': '456',
                        'items': [{'price': {'regular': 2.49}, 'size': '2 units'}]
                    }
                ]
            }
        ]

        # Instantiate ShoppingCart with any store_location_id (mocked)
        cart = ShoppingCart('fake_store_id')

        # Call price_ingredients with a small list
        result = cart.price_ingredients(['ingredient1', 'ingredient2'])

        # Check that each ingredient exists in results
        self.assertIn('ingredient1', result)
        self.assertIn('ingredient2', result)

        # Check the structure of the returned product dicts
        for ing, products in result.items():
            for product in products:
                self.assertIn('description', product)
                self.assertIn('price', product)
                self.assertIn('size', product)
                self.assertIn('product_id', product)
                self.assertIsInstance(product['price'], float)

        # Optional: check values match the mocked data
        self.assertEqual(result['ingredient1'][0]['description'], 'Mock Ingredient 1')
        self.assertEqual(result['ingredient1'][0]['price'], 1.99)
        self.assertEqual(result['ingredient1'][0]['size'], '1 unit')
        self.assertEqual(result['ingredient1'][0]['product_id'], '123')

        self.assertEqual(result['ingredient2'][0]['description'], 'Mock Ingredient 2')
        self.assertEqual(result['ingredient2'][0]['price'], 2.49)
        self.assertEqual(result['ingredient2'][0]['size'], '2 units')
        self.assertEqual(result['ingredient2'][0]['product_id'], '456')


if __name__ == '__main__':
    unittest.main()