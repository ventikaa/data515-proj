from kroger_api import KrogerAPI
from kroger_api.utils.env import load_and_validate_env, get_zip_code
from dotenv import load_dotenv
from pathlib import Path 

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

load_and_validate_env(["KROGER_CLIENT_ID", "KROGER_CLIENT_SECRET"])

zip_code = get_zip_code("98034")

kroger = KrogerAPI()

# Get a client credentials token for public data
token_info = kroger.authorization.get_token_with_client_credentials("product.compact")

locations = kroger.location.search_locations(
                zip_code=zip_code,
                radius_in_miles=10,
                limit=1
            )

# Search for products
products = kroger.product.search_products(
        term="milk",
        location_id=locations["data"][0]["locationId"],
        limit=5
    )

print(f"Found {len(products['data'])} products!")

print(products['data'][0])