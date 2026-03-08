"""
Unit tests for the kroger_shopping_cart module.
"""

import unittest
from unittest.mock import patch
from api import kroger_shopping_cart


class TestKrogerShoppingCart(unittest.TestCase):
    """Test cases for the ShoppingCart class."""

    @patch("api.kroger_shopping_cart.init_kroger_env")
    @patch("api.kroger_shopping_cart.KrogerAPI")
    def test_price_ingredients(self, mock_kroger_api, mock_init_env):
        """Test that price_ingredients returns structured product data."""
        mock_init_env.return_value = None

        mock_api_instance = mock_kroger_api.return_value
        mock_api_instance.product.search_products.side_effect = [
            {
                "data": [
                    {
                        "description": "Mock Ingredient 1",
                        "productId": "123",
                        "items": [{"price": {"regular": 1.99}, "size": "1 unit"}],
                    }
                ]
            },
            {
                "data": [
                    {
                        "description": "Mock Ingredient 2",
                        "productId": "456",
                        "items": [{"price": {"regular": 2.49}, "size": "2 units"}],
                    }
                ]
            },
        ]

        cart = kroger_shopping_cart.ShoppingCart("fake_store_id")

        result = cart.price_ingredients(["ingredient1", "ingredient2"])

        self.assertIn("ingredient1", result)
        self.assertIn("ingredient2", result)

        for products in result.values():
            for product in products:
                self.assertIn("description", product)
                self.assertIn("price", product)
                self.assertIn("size", product)
                self.assertIn("product_id", product)
                self.assertIsInstance(product["price"], float)

        self.assertEqual(result["ingredient1"][0]["description"], "Mock Ingredient 1")
        self.assertEqual(result["ingredient1"][0]["price"], 1.99)
        self.assertEqual(result["ingredient1"][0]["size"], "1 unit")
        self.assertEqual(result["ingredient1"][0]["product_id"], "123")

        self.assertEqual(result["ingredient2"][0]["description"], "Mock Ingredient 2")
        self.assertEqual(result["ingredient2"][0]["price"], 2.49)
        self.assertEqual(result["ingredient2"][0]["size"], "2 units")
        self.assertEqual(result["ingredient2"][0]["product_id"], "456")


if __name__ == "__main__":
    unittest.main()
