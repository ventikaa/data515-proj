from kroger_api import KrogerAPI
from api.kroger_auth import init_kroger_env


class KrogerStoreLocator:
    """
    Responsible ONLY for turning a ZIP code into nearby stores.
    """

    def __init__(self, zip_code: str, radius: int = 10, limit: int = 5):
        init_kroger_env()

        self.zip_code = zip_code
        self.radius = radius
        self.limit = limit

        self.kroger = KrogerAPI()
        self.kroger.authorization.get_token_with_client_credentials(
            "product.compact"
        )

    def get_stores(self) -> list[dict]:
        """
        Returns a simplified list of stores suitable for UI dropdowns.
        """
        response = self.kroger.locations.search(
            zipCode=self.zip_code,
            radiusInMiles=self.radius,
            limit=self.limit,
        )

        stores = []
        for loc in response.get("data", []):
            stores.append({
                "location_id": loc["locationId"],
                "name": loc["name"],
                "address": f'{loc["address"]["addressLine1"]}, '
                           f'{loc["address"]["city"]}, '
                           f'{loc["address"]["state"]}',
            })

        return stores