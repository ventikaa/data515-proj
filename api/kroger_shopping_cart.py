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

                products.append({
                    "description": item.get("description"),
                    "price": price_info.get("regular"),
                    "size": item.get("items", [{}])[0].get("size"),
                    "product_id": item.get("productId"),
                })

            results[ingredient] = products

        return results