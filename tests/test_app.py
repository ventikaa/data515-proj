"""
Unit tests for the Cooking Helper Dash Application.
"""

import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
import dash
import pytest
from hypothesis import given, strategies as st

from app.app import parse_r_list, update_recipes, add_to_cart

# -----------------------------
# pytest fixtures
# -----------------------------

@pytest.fixture
def mock_shopping_cart(monkeypatch):
    """Mock shopping cart creation"""
    mock_cart = MagicMock()

    mock_cart.price_ingredients.return_value = ["milk"]
    mock_cart.get_cheapest_ingredients.return_value = {
        "milk": {"description": "Mock Milk", "price": 3.99}
    }

    monkeypatch.setattr("app.app.ShoppingCart", lambda store_id: mock_cart)

    return mock_cart


# -----------------------------
# Unit Tests
# -----------------------------

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

    @patch("app.app.DF", new=pd.DataFrame({
        "Name": ["Apple Pie", "Beef Stew"],
        "RecipeCategory": ["Dessert", "Main"],
        "RecipeIngredientParts": [["apple"], ["beef"]],
        "RecipeIngredientQuantities": [["1"], ["1"]],
        "Description": ["Yummy", "Hearty"],
        "RecipeServings": [8, 4],
        "Images": [[], []]
    }))
    def test_update_recipes_filtering(self):
        """Test to update the recipe filtering"""
        _, count_msg = update_recipes("Apple", "All")
        self.assertIn("Found 1 recipes", count_msg)

    @patch("app.app.dash.callback_context")
    def test_add_to_cart_no_store(self, mock_ctx):
        """Test that add_to_cart triggers a toast if no store_id is provided."""

        mock_ctx.triggered = [{'prop_id': '{"type":"add-btn","index":0}.n_clicks'}]

        n_clicks = [1]

        _, pathname, toast_open = add_to_cart(
            n_clicks,
            {},
            None
        )

        self.assertTrue(toast_open)
        self.assertEqual(pathname, dash.no_update)

    @given(st.text())
    def test_parse_r_list_fuzzing(self, s):
        """Ensures the parser never crashes, regardless of the input string."""
        result = parse_r_list(s)
        self.assertIsInstance(result, list)
