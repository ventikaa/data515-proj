"""
Cooking Helper Dash Application.
Finds recipes and fetches real-time Kroger prices based on user location.
"""

import json
import re
import sys
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import ALL, Input, Output, State, callback, dcc, html
from kroger_api import KrogerAPI

# --- Setup System Path ---
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
# Internal API imports
from api.kroger_shopping_cart import ShoppingCart
from api.kroger_store_locator import KrogerStoreLocator

# --- 1. Custom Aesthetic Styles ---
COLORS = {
    "background": "#FFF9F5",  # Soft Cream
    "primary": "#FF8A8A",     # Muted Coral
    "secondary": "#95BDFF",   # Pastel Blue
    "accent": "#B4E4FF",      # Baby Blue
    "text": "#4A4A4A",        # Soft Charcoal
    "white": "#FFFFFF"
}
FONT_STYLE = {"fontFamily": "'Quicksand', sans-serif"}


def parse_r_list(r_string):
    """Parses R-formatted strings from the CSV into Python lists."""
    if pd.isna(r_string) or not isinstance(r_string, str) or r_string == "character(0)":
        return []

    content = re.sub(r'^c\(', '', r_string)
    content = re.sub(r'\)$', '', content)

    # This finds all text inside quotes
    parts = re.findall(r'"([^"]*)"', content)

    # Removes any steps that are just commas, spaces, or empty
    parts = [p.strip() for p in parts if p.strip() and p.strip() != ","]
    parts = [p.replace('\\', '').strip() for p in parts if p.strip() and p.strip() != ","]
    if not parts and content.strip():
        return [content.strip()]

    return parts


def get_kroger_pricing_with_id(ingredient_list, location_id):
    """Fetches pricing for ingredients at a specific Kroger location."""
    kroger = KrogerAPI()
    kroger.authorization.get_token_with_client_credentials("product.compact")

    results = {}
    for ingredient in ingredient_list:
        products = kroger.product.search_products(term=ingredient, location_id=location_id, limit=5)
        valid = []
        for p in products.get("data", []):
            desc = p['description']
            for item in p['items']:
                price = item.get('price', {}).get('regular')
                stock = item.get('inventory', {}).get('stockLevel')
                if price and stock != "TEMPORARILY_OUT_OF_STOCK":
                    valid.append({"description": desc, "price": float(price)})

        if valid:
            results[ingredient] = sorted(valid, key=lambda x: x['price'])[0]
        else:
            results[ingredient] = {"description": "Not available", "price": 0.0}
    return results


# --- Load Data ---
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "data.csv"
DF = pd.read_csv(CSV_PATH)

DF['RecipeIngredientParts'] = DF['RecipeIngredientParts'].apply(parse_r_list)
DF['RecipeIngredientQuantities'] = DF['RecipeIngredientQuantities'].apply(parse_r_list)
DF['Images'] = DF['Images'].apply(parse_r_list)
DF['RecipeInstructions'] = DF['RecipeInstructions'].apply(parse_r_list)

# --- App Initialization ---
app = dash.Dash(__name__,
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP,
                    "https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap"
                ],
                suppress_callback_exceptions=True)

app.layout = html.Div(style={"backgroundColor": COLORS["background"],
                             "minHeight": "100vh", **FONT_STYLE}, children=[
    dcc.Store(id='cart-store', data={}, storage_type='session'),
    dcc.Store(id='store-id-store', data=None, storage_type='session'),

    dcc.Loading(
        id="global-loading",
        type="circle",
        color=COLORS["primary"],
        fullscreen=True,
        children=[
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ]
    )
])


# --- 4. Page Layouts ---
def recipe_finder_layout():
    """Renders the main recipe search and store location page."""
    categories = ["All"] + sorted(DF['RecipeCategory'].dropna().unique().tolist())
    return dbc.Container([
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Select Your Kroger Store")),
            dbc.ModalBody(id="store-selector-body"),
        ], id="store-modal", is_open=False, size="lg"),

        html.Div([
            dbc.Toast(
                "Please enter your zip code and select a store first! 📍",
                id="store-warning-toast",
                header="Store Required",
                is_open=False,
                dismissable=True,
                duration=4000,
                icon="danger",
                style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
            ),
        ]),

        dbc.Row([
            dbc.Col([
                html.H1("✨ Cooking Helper", style={"color": COLORS["primary"],
                                                   "fontWeight": "600", "marginTop": "30px"}),
                html.P("Find recipes and check real-time Kroger prices", className="text-muted"),
            ], width=9),
            dbc.Col(dbc.Button("🛒 My Cart", href="/cart",
                               style={"backgroundColor": COLORS["secondary"],
                                      "border": "none", "borderRadius": "20px",
                                      "marginTop": "40px"}), width=3)
        ]),

        dbc.Row([
            dbc.Col([
                html.Div(style={"backgroundColor": COLORS["white"],
                                "padding": "20px",
                                "borderRadius": "20px",
                                "boxShadow": "0 4px 6px rgba(0,0,0,0.05)"},
                         children=[
                    html.H5("📍 Store Location", style={"color": COLORS["text"]}),
                    html.Div(id="zip-container", children=[
                        dbc.Input(id="zip-input",
                                  placeholder="Enter Zip Code",
                                  type="number",
                                  style={"borderRadius": "10px"},
                                  className="mt-2"),
                        dbc.Button("Find Stores",
                                   id="find-stores-btn",
                                   color="info",
                                   size="sm",
                                   className="mt-2 w-100",
                                   style={"borderRadius": "10px",
                                          "backgroundColor": COLORS["secondary"],
                                          "border": "none"}),
                    ]),
                    html.Div(id="change-loc-container",
                             style={"display": "none"},
                             children=[
                        dbc.Button("🔄 Change Location",
                                   id="change-loc-btn",
                                   color="secondary",
                                   outline=True,
                                   size="sm",
                                   className="mt-2 w-100",
                                   style={"borderRadius": "10px"}),
                        html.Div(id="selected-store-display",
                                 className="mt-2 small text-success",
                                 style={"fontWeight": "bold"}),
                    ]),
                    html.Hr(className="my-4"),
                    html.H5("Filter Recipes", style={"color": COLORS["text"]}),
                    dbc.Input(id="search-query",
                              placeholder="Search ingredients...",
                              style={"borderRadius": "10px"},
                              className="mt-2"),
                    dcc.Dropdown(id="category-dropdown",
                                 options=categories,
                                 value="All",
                                 className="mt-3",
                                 style={"borderRadius": "10px"}),
                    html.Div(id="recipe-count",
                             className="mt-3 text-muted",
                             style={"fontSize": "0.8rem"})
                ])
            ], width=3),
            dbc.Col(html.Div(id="recipe-display-area"), width=9)
        ])
    ])


def shopping_cart_layout():
    """Renders the shopping cart page with recipe instructions and prices."""
    return dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Button("← Home", href="/",
                               color="link",
                               style={"color": COLORS["primary"],
                                      "marginTop": "30px",
                                      "textDecoration": "none"}), width=2),

            dbc.Col(html.H1("🌸 Your Shopping List",
                            style={"color": COLORS["primary"],
                                   "marginTop": "30px"}), width=7),

            dbc.Col(dbc.Button("🗑️ Clear Cart",
                               id="clear-cart-btn",
                               color="danger",
                               outline=True,
                               style={"borderRadius": "20px",
                                      "marginTop": "40px",
                                      "fontSize": "0.8rem"}), width=3)
        ]),
        dbc.Row([
            dbc.Col(id="cart-container", width={"size": 10, "offset": 1},
                    style={"backgroundColor": COLORS["white"],
                           "padding": "30px",
                           "borderRadius": "30px",
                           "marginTop": "20px",
                           "boxShadow": "0 4px 15px rgba(0,0,0,0.05)"})
        ])
    ])


# --- 5. Callbacks ---

@callback(
    Output("zip-container", "style"),
    Output("change-loc-container", "style"),
    Output("store-id-store", "data", allow_duplicate=True),
    Input("change-loc-btn", "n_clicks"),
    Input("store-id-store", "data"),
    prevent_initial_call=True
)
def manage_location_ui(_, store_id):
    """Toggles visibility between zip code input and chosen store display."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == "change-loc-btn":
        return {"display": "block"}, {"display": "none"}, None

    if store_id:
        return {"display": "none"}, {"display": "block"}, dash.no_update

    return {"display": "block"}, {"display": "none"}, dash.no_update


def toggle_location_button(store_id):
    """Returns style and label configurations based on store selection status."""
    if not store_id:
        return {"display": "block"}, "Find Stores", "info", False
    return {"display": "none"}, "🔄 Change Location", "secondary", True


@callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    """Router for multi-page navigation."""
    if pathname == '/cart':
        return shopping_cart_layout()
    return recipe_finder_layout()


@callback(
    Output("recipe-display-area", "children"),
    Output("recipe-count", "children"),
    Input("search-query", "value"),
    Input("category-dropdown", "value")
)
def update_recipes(search, cat):
    """Filters recipe dataframe and renders cards based on user search."""
    filt = DF.head(30).copy()
    if cat and cat != "All":
        filt = filt[filt['RecipeCategory'] == cat]
    if search:
        filt = filt[filt['Name'].str.contains(search, case=False) |
                    filt['RecipeIngredientParts'].astype(str).str.contains(search, case=False)]

    cards = []
    for idx, row in filt.iterrows():
        ing_items = []
        for q, p in zip(row['RecipeIngredientQuantities'], row['RecipeIngredientParts']):
            q_str = str(q).strip() if pd.notna(q) and str(q).lower() != 'nan' else ""
            ing_items.append(html.Li(f"{q_str} {p}" if q_str else p,
                                     style={"fontSize": "0.85rem"}))

        servings = html.Span(f" 🍽️ {int(row['RecipeServings'])} servings",
                             style={"fontSize": "0.8rem",
                                    "color": COLORS["secondary"]}) \
                             if pd.notna(row['RecipeServings']) else None
        image_urls = row['Images']
        col_w, img_col = (4, dbc.Col([html.Img(src=image_urls[0],
                                               style={"width": "100%",
                                                      "borderRadius": "15px"})],
                                     width=4)) if image_urls else (6, None)

        cards.append(html.Div(style={"backgroundColor": COLORS["white"],
                                     "borderRadius": "25px", "padding": "20px",
                                     "marginBottom": "25px",
                                     "boxShadow": "0 4px 15px rgba(0,0,0,0.05)"},
                              children=[
            html.H4(row['Name'], style={"color": COLORS["text"], "fontWeight": "600"}),
            dbc.Row([
                dbc.Col([html.H6("Ingredients", style={"color": COLORS["primary"]}),
                         html.Ul(ing_items[:10])], width=col_w),
                dbc.Col([html.H6("About", style={"color": COLORS["primary"]}), servings,
                         html.P(row['Description'],
                                style={"fontSize": "0.8rem", "marginTop": "5px"})], width=col_w),
                img_col
            ]),
            dbc.Button("✨ Calculate Price", id={'type': 'add-btn', 'index': idx},
                       style={"backgroundColor": COLORS["primary"], "border": "none",
                              "borderRadius": "15px", "marginTop": "10px"})
        ]))
    return cards, f"Found {len(filt)} recipes"


@callback(
    Output("store-modal", "is_open"),
    Output("store-selector-body", "children"),
    Input("find-stores-btn", "n_clicks"),
    State("zip-input", "value"),
    prevent_initial_call=True
)
def find_stores(_, zip_code):
    """Fetches store locations from zip code and renders selection cards."""
    if not zip_code:
        return True, "Please enter a zip code first."

    store_locator = KrogerStoreLocator(zip_code)
    store_locations = store_locator.get_stores()

    if not store_locations:
        return True, html.Div([
            html.P("No Kroger stores found nearby. Try a different zip code!",
                   style={"color": "red", "fontWeight": "bold", "textAlign": "center"})
        ])

    store_options = []
    for store in store_locations:
        store_options.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6(f"{store['chain'].capitalize()} - {store['name']}"),
                    html.P(store['address'], className="small text-muted"),
                    dbc.Button("Select This Store",
                               id={'type': 'select-store-btn',
                                   'id': store['location_id'],
                                   'name': store['name']}, color="primary", size="sm"),
                ])
            ], className="mb-2")
        )

    return True, store_options


@callback(
    Output("store-id-store", "data"),
    Output("store-modal", "is_open", allow_duplicate=True),
    Output("selected-store-display", "children"),
    Input({'type': 'select-store-btn', 'id': ALL, 'name': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def save_store(n_clicks):
    """Saves the selected store ID to the user's session store."""
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks):
        return dash.no_update, dash.no_update, dash.no_update

    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    selected_id = button_id['id']
    selected_name = button_id['name']

    return selected_id, False, f"📍 {selected_name}"


@callback(
    Output('cart-store', 'data', allow_duplicate=True),
    Output('url', 'pathname', allow_duplicate=True),
    Output('store-warning-toast', 'is_open'),
    Input({'type': 'add-btn', 'index': ALL}, 'n_clicks'),
    State('cart-store', 'data'),
    State('store-id-store', 'data'),
    prevent_initial_call=True
)
def add_to_cart(n_clicks, cart_data, store_id):
    """Fetches Kroger prices for a recipe and adds it to the session cart."""
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks):
        return cart_data, dash.no_update, False

    if not store_id:
        return cart_data, dash.no_update, True

    if not isinstance(cart_data, dict):
        cart_data = {}

    if 'items' not in cart_data:
        cart_data['items'] = {}

    if 'recipes' not in cart_data:
        cart_data['recipes'] = []

    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    idx = button_id['index']
    ingredients = DF.iloc[idx]['RecipeIngredientParts']

    shopping_cart = ShoppingCart(store_id)
    ingredients_list = shopping_cart.price_ingredients(ingredients)
    shopping_cart.get_cheapest_ingredients(ingredients_list)
    recipe_row = DF.iloc[idx]

    recipe_info = {
        "name": recipe_row['Name'],
        "ingredients": list(zip(recipe_row['RecipeIngredientQuantities'],
                                recipe_row['RecipeIngredientParts'])),
        "instructions": recipe_row['RecipeInstructions']
    }

    cart_data['recipes'] = [recipe_info]
    cart_data['items'] = {}

    real_prices = get_kroger_pricing_with_id(recipe_row['RecipeIngredientParts'], store_id)

    for ing, data in real_prices.items():
        cart_data['items'][ing] = {
            "description": data["description"],
            "price": data["price"],
            "qty": 1
        }

    return cart_data, '/cart', False


@callback(
    Output('cart-store', 'data', allow_duplicate=True),
    Input('clear-cart-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_cart(n_clicks):
    """Wipes the current cart data."""
    if n_clicks:
        return {}
    return dash.no_update


@callback(
    Output('cart-store', 'data'),
    Input({'type': 'cart-item-btn', 'action': ALL, 'item': ALL}, 'n_clicks'),
    State('cart-store', 'data'),
    prevent_initial_call=True
)
def update_cart_quantities(n_clicks, cart):
    """Increments, decrements, or removes items from the shopping cart."""
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks):
        return cart

    btn_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    action, item_key = btn_id['action'], btn_id['item']

    if 'items' in cart and item_key in cart['items']:
        if action == 'plus':
            cart['items'][item_key]['qty'] += 1
        elif action == 'minus':
            if cart['items'][item_key]['qty'] > 1:
                cart['items'][item_key]['qty'] -= 1
            else:
                del cart['items'][item_key]
        elif action == 'delete':
            del cart['items'][item_key]

    return cart


@callback(
    Output('cart-container', 'children'),
    Input('cart-store', 'data')
)
def render_cart(cart_data):
    """Renders the final shopping cart UI from stored session data."""
    if not cart_data or not cart_data.get('items'):
        return html.Div("Your basket is empty! ✨", className="text-center mt-5")

    recipe_sections = []
    for recipe in cart_data.get('recipes', []):
        recipe_sections.append(html.Div(
            style={"marginBottom": "30px", "borderBottom": f"1px solid {COLORS['background']}",
                   "paddingBottom": "20px"}, children=[
            html.H3(f"📖 {recipe['name']}", style={"color": COLORS["text"]}),
            dbc.Row([
                dbc.Col([
                    html.H6("Original Ingredients", style={"color": COLORS["primary"]}),
                    html.Ul([html.Li(f"{q} {i}", style={"fontSize": "0.85rem"})
                             for q, i in recipe['ingredients']])
                ], width=4),
                dbc.Col([
                    html.H6("Instructions", style={"color": COLORS["primary"]}),
                    html.Ol([html.Li(step, style={"fontSize": "0.85rem", "marginBottom": "5px"})
                             for step in recipe['instructions']])
                ], width=8)
            ])
        ]))

    table_rows, grand_total = [], 0
    for item, info in cart_data['items'].items():
        desc = info.get('description', 'Kroger Item')
        price = info.get('price', 0.0)
        qty = info.get('qty', 1)
        subtotal = qty * price
        grand_total += subtotal

        table_rows.append(html.Tr([
            html.Td([html.B(item), html.Br(), html.Small(desc, className="text-muted")]),
            html.Td([
                dbc.ButtonGroup([
                    dbc.Button("-", id={'type': 'cart-item-btn', 'action': 'minus', 'item': item},
                               size="sm", color="light"),
                    html.Span(f" {qty} ", className="mx-3", style={"lineHeight": "31px"}),
                    dbc.Button("+", id={'type': 'cart-item-btn', 'action': 'plus', 'item': item},
                               size="sm", color="light"),
                ])
            ], style={"textAlign": "center"}),
            html.Td(f"${price:.2f}", style={"textAlign": "right"}),
            html.Td(f"${subtotal:.2f}", style={"textAlign": "right", "fontWeight": "600"}),
            html.Td(dbc.Button("×", id={'type': 'cart-item-btn', 'action': 'delete', 'item': item},
                               color="light", size="sm", style={"borderRadius": "50%"}))
        ]))

    table_rows.append(html.Tr([
        html.Td("Grand Total", colSpan=3,
                style={"fontWeight": "600", "color": COLORS["primary"], "fontSize": "1.2rem"}),
        html.Td(f"${grand_total:.2f}",
                style={"fontWeight": "700", "color": COLORS["primary"],
                       "fontSize": "1.2rem", "textAlign": "right"}),
        html.Td("")
    ]))

    pricing_table = dbc.Table([
        html.Thead(html.Tr([html.Th("Item"), html.Th("Qty", className="text-center"),
                            html.Th("Price", className="text-end"),
                            html.Th("Subtotal", className="text-end"), html.Th("")])),
        html.Tbody(table_rows)
    ], borderless=True, hover=True)

    return html.Div([
        html.Div(recipe_sections),
        html.Hr(style={"margin": "40px 0", "borderTop": f"2px solid {COLORS['primary']}"}),
        html.H3("🛒 Kroger Price Summary", style={"marginBottom": "20px"}),
        pricing_table
    ])


if __name__ == "__main__":
    app.run(debug=True)
