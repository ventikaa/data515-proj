import dash
from dash import html
import pandas as pd
from pathlib import Path
from api.kroger_shopping_cart import ShoppingCart

# Register the page with both path and path_template
dash.register_page(
    __name__,
    path="/recipes/<recipe_id>",         # URL pattern users will visit
    path_template="/recipes/<recipe_id>" # tells Dash this is a dynamic page
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_path = BASE_DIR / "data" / "data.csv"

df = pd.read_csv(csv_path)



# Parse lists as you did in home.py
import re
def parse_r_list(r_string):
    if pd.isna(r_string) or not isinstance(r_string, str):
        return []
    content = re.sub(r'^c\(', '', r_string)
    content = re.sub(r'\)$', '', content)
    return re.findall(r'"([^"]*)"', content)

df['RecipeIngredientParts'] = df['RecipeIngredientParts'].apply(parse_r_list)
df['RecipeIngredientQuantities'] = df['RecipeIngredientQuantities'].apply(parse_r_list)
df['RecipeInstructions'] = df['RecipeInstructions'].apply(parse_r_list)



def layout(recipe_id=None):
    if recipe_id is None:
        return html.Div("No recipe selected.")

    # recipe_id comes from URL, convert to int
    recipe_id = int(recipe_id)

    # Get the row by dataframe index
    row = df[df["RecipeId"] == recipe_id]

    # Build ingredients and instructions
    ingredients = [html.Li(f"{qty} {part}") for qty, part in zip(row['RecipeIngredientQuantities'], row['RecipeIngredientParts'])]
    instructions = [html.P(f"{i+1}. {step}") for i, step in enumerate(row['RecipeInstructions'])]

    # Shopping cart stuff
    shopping_cart = ShoppingCart("70100391")
    ingredients_dict = shopping_cart.price_ingredients(["fresh mushrooms",
        "butter",
        "chicken breast",
        "flour",
        "marsala",
        "chicken broth",
        "salt",
        "mozarella cheese",
        "parmesan cheese",
        "green onion"
    ])

    print(ingredients_dict)

    return html.Div([
        html.H2(row['Name']),
        html.H4("Ingredients"),
        html.Ul(ingredients),
        html.H4("Instructions"),
        html.Div(instructions),
        html.Br(),
        html.H3("💰 Price Calculation Goes Here"),
        html.Br(),
        html.A("⬅ Back to Home", href="/")
    ])