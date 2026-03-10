"""
Unit tests for the Cooking Helper Dash Application.
"""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
from hypothesis import given, strategies as st
from dash.testing.application_runners import import_app

from app import parse_r_list, update_recipes, add_to_cart

class TestCookingHelper(unittest.TestCase):
    """Test suite for data processing and callback logic."""

    def test_parse_r_list_valid(self):
        """Test parsing a standard R-style character vector string."""
        r_string = 'c("Butter", "Sugar", "Flour")'
        expected = ["Butter", "Sugar", "Flour"]
        self.assertEqual(parse_r_list(r_string), expected)

    def test_parse_r_list_empty(self):
        """Test parsing an empty R character vector."""
        self.assertEqual(parse_r_list("character(0)"), [])
        self.assertEqual(parse_r_list(None), [])

    @patch('app.app2.DF')
    def test_update_recipes_filtering(self, mock_df):
        """Test that update_recipes correctly filters by search term."""
        mock_data = pd.DataFrame({
            'Name': ['Apple Pie', 'Beef Stew'],
            'RecipeCategory': ['Dessert', 'Main'],
            'RecipeIngredientParts': [['apple'], ['beef']],
            'RecipeIngredientQuantities': [['1'], ['1']],
            'Description': ['Yummy', 'Hearty'],
            'RecipeServings': [8, 4],
            'Images': [[], []]
        })
        mock_df.head.return_value = mock_data
        
        # Test search filter
        cards, count_msg = update_recipes("Apple", "All")
        self.assertIn("Found 1 recipes", count_msg)
        self.assertEqual(len(cards), 1)

    @patch('app.app2.get_kroger_pricing_with_id')
    @patch('app.app2.ShoppingCart')
    @patch('app.app2.DF')
    def test_add_to_cart_no_store(self, mock_df, mock_cart_class, mock_pricing):
        """Test that add_to_cart triggers a toast if no store_id is provided."""
        n_clicks = [1] 

        cart_data, pathname, toast_open = add_to_cart(n_clicks, {}, None)
        
        self.assertTrue(toast_open)
        self.assertEqual(pathname, dash.no_update)

    def test_001_layout_loads(dash_duo):
        """Check that the app header loads correctly."""
        app = import_app("app.app2")
        dash_duo.start_server(app)

        dash_duo.wait_for_text_to_equal("h1", "✨ Cooking Helper", timeout=10)
    
        # Check if the zip input exists
        assert dash_duo.find_element("#zip-input") is not None

    @pytest.fixture
    def mock_kroger_api(monkeypatch):
        """Replaces the real KrogerAPI with a fake version for all tests."""
        mock = MagicMock()
        mock.product.search_products.return_value = {
            "data": [{
                "description": "Mocked Milk",
                "items": [{"price": {"regular": "3.99"}}]
            }]
        }
        # Apply the mock to the specific path in your app
        monkeypatch.setattr("app.app2.KrogerAPI", lambda: mock)
        return mock

    @given(st.text())
    def test_parse_r_list_fuzzing(s):
        """Ensures the parser never crashes, regardless of the input string."""
        result = parse_r_list(s)
        assert isinstance(result, list)

    def test_full_navigation_flow(dash_duo, mock_kroger_data):
        """Tests the user journey from Home to Cart."""
        # Start the app
        app = import_app("app.app2")
        dash_duo.start_server(app)

        # 1. Enter Zip Code
        zip_input = dash_duo.find_element("#zip-input")
        zip_input.send_keys("98105")
        dash_duo.find_element("#find-stores-btn").click()

        # 2. Wait for Modal and select a store
        dash_duo.wait_for_element("#store-modal", timeout=5)
        dash_duo.find_element(".btn-primary").click() # Select first store

        # 3. Click Calculate Price on the first recipe card
        # Use a CSS selector that targets your pattern-matching ID
        dash_duo.find_elements("button")[2].click() 

        # 4. Assert URL changed and Cart loaded
        dash_duo.wait_for_page("/cart", timeout=10)
        assert "Your Shopping List" in dash_duo.find_element("h1").text