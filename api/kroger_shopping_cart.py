"""
Kroger shopping cart backend component
Builds the "shopping_cart" ingredients dict that the front-end will display
"""
from kroger_api import KrogerAPI
from api.kroger_auth import init_kroger_env


class ShoppingCart:
    """
    Store-scoped pricing logic.
    No ZIP code.
    No Dash state.
    """

    def __init__(self, store_location_id: str):
        init_kroger_env()

        self.store_location_id = store_location_id

        self.kroger = KrogerAPI()
        self.kroger.authorization.get_token_with_client_credentials(
            "product.compact"
        )

    def price_ingredients(
        self,
        ingredients: list[str],
        limit_per_ingredient: int = 3,
    ) -> dict:
        """
        Prices ingredients at the selected store.

        Returns:
        {
            "milk": [
                {"description": "...", "price": 3.49, "size": "1 gal"},
                ...
            ],
            ...
        }
        """
        results: dict[str, list[dict]] = {}

        for ingredient in ingredients:
            response = self.kroger.product.search_products(
                term=ingredient,
                location_id=self.store_location_id,
                limit=limit_per_ingredient,
            )

            products = []
            for item in response.get("data", []):
                price_info = item.get("items", [{}])[0].get("price", {})
                
                price = price_info.get("regular") or -1
                if price > 0:
                    products.append({
                        "description": item.get("description"),
                        "price": price,
                        "size": item.get("items", [{}])[0].get("size"),
                        "product_id": item.get("productId"),
                    })

            results[ingredient] = products

        return results

    def get_cheapest_ingredients(self, ingredient_list: list[str]) -> dict:
        """
        Returns the cheapest valid product per ingredient for this store.
        """
        all_products = self.price_ingredients(ingredient_list, limit_per_ingredient=5)

        cheapest_dict = {}
        for ing, products in all_products.items():
            if isinstance(products, list) and products:
                # Sort by price and take the first (cheapest)
                
                # print(products)
                sorted_products = sorted(products, key=lambda x: x["price"])
                cheapest_dict[ing] = sorted_products[0]
            else:
                # Fallback if no products found
                cheapest_dict[ing] = {"description": "Not available", "price": 0.0}

        return cheapest_dict