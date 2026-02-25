from kroger_api import KrogerAPI
from kroger_api.utils.env import load_and_validate_env, get_zip_code
from dotenv import load_dotenv
from pathlib import Path 
import json

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

load_and_validate_env(["KROGER_CLIENT_ID", "KROGER_CLIENT_SECRET"])

def main():
    # Please enter your zip code
    zip_code = input("Enter your zip code: ")

    try: 
        if len(zip_code) != 5:
            raise ValueError("Not proper zip_code. Please enter a 5 digit integer")
        
        zip_code = int(zip_code)
    except ValueError:
        print("Invalid zip_code, please try again")
        zip_code = "98034"
    
    kroger = KrogerAPI()

    # Get a client credentials token for public data
    token_info = kroger.authorization.get_token_with_client_credentials("product.compact")
    locations = kroger.location.search_locations(
                zip_code=zip_code,
                radius_in_miles=10,
                limit=5
    )

    # Parsing through location information
    print("Showing the closest locations to you")
    location_id_dict = {}
    i = 1
    for location in locations.get("data", []):
        # print(location)
        location_id_dict[i] = location['locationId']
        print('-' * 50)
        print(f'LOCATION #{i}')
        print(f'Location ID: {location["locationId"]}')
        print(f'Chain: {location["chain"]}')
        print(f'Name: {location["name"]}')
        print(f"Address: {location['address']['addressLine1']} {location['address']['city']}, {location['address']['state']}, {location['address']['zipCode']}")
        print('-' * 50)
        i += 1
    
    store_number_selector_valid = False 
    while not store_number_selector_valid:
        try:
            store_number_selector = input("Please select one of the following locations to choose from:")
            store_number_selector = int(store_number_selector)
            if store_number_selector >= 1 and store_number_selector <= 5:
                store_number_selector_valid = True
                store_location_id = location_id_dict[store_number_selector]
        except:
            print("Input value not accepted, please try again.")

    
    # mock recipe data below
    mock_recipe_ingredients = [
        # "c(""fresh mushrooms"", ""butter"", ""boneless skinless chicken breast halves"", ""flour"", ""butter"", ""marsala"", ""chicken broth"", ""salt"", ""mozzarella cheese"", ""parmesan cheese"", ""green onion"""
        "fresh mushrooms",
        "butter",
        # "boneless skinless chicken breast halves",
        "chicken breast",
        "flour",
        "marsala",
        "chicken broth",
        "salt",
        "mozarella cheese",
        "parmesan cheese",
        "green onion"
    ] 

    print('#' * 50)
    print('Obtaining ingredients below:')
    print('#' * 50)

    ingredient_dict = {}
    for ingredient in mock_recipe_ingredients:

        print(f"Searching for: {ingredient}")
        ingredient_dict[ingredient] = []

        products = kroger.product.search_products(
            term=ingredient,
            location_id=store_location_id,
            limit=5
        )

        print(f"{ingredient} responses")
        for product in (products.get("data", [])):
            print('-' * 50)
            print(product['description'])
            for item in product['items']:
                price = item.get('price', {}).get('regular', 'PRICE UNAVAILABLE')

                # If there's no stock level, treating it as same as temporarily out of stock
                inventory = item.get('inventory', {}).get('stockLevel', 'TEMPORARILY_OUT_OF_STOCK')
                print(f"Price: ${price}, Inventory: {inventory}")

            if (inventory != "TEMPORARILY_OUT_OF_STOCK"):
                ingredient_dict[ingredient].append((product['description'], price, inventory))
                
            # print(product['itemInformation'])
            print('-' * 50)
            
        print()
    
    print(ingredient_dict)
    
    # Creating the "shopping cart"
    print("CREATING SHOPPING CART")
    for k, v in ingredient_dict.items():
        # print(f"Ingredient: {k}")
        if len(v) == 0:
            # print("Unfortunately we couldn't find the specified ingredient")
            continue
        else:
            sorted_v = sorted(v, key = lambda x: x[1])
            # print(sorted_v[0])
            ingredient_dict[k] = sorted_v
    
    recipe_sum = 0
    missing_ingredients = []
    for k, v in ingredient_dict.items():
        if len(v) > 0:
            print(f'{k}: {v[0]}')
            recipe_sum += v[0][1]
        else:
            print(f'{k}: Unfortunately, item could not be found')
            missing_ingredients.append(k)
    
    print()

    print("FINAL SUMMARY:")
    print('-' * 50)
    print(f'TOTAL RECIPE COST: {recipe_sum}')

    if len(missing_ingredients) > 0:
        print(f"DISCLAIMER! The following ingredients were not found: {missing_ingredients}. User will need to locate it"
        " and the price is not accounted for in the recipe cost.")
    

if __name__ == "__main__":
    main()