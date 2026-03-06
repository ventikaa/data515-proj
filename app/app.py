import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from kroger_api import KrogerAPI
import pandas as pd
import re
import dash
import json
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc
from api.kroger_shopping_cart import ShoppingCart
from api.kroger_store_locator import KrogerStoreLocator


# root_dir = Path(__file__).resolve().parent.parent
# sys.path.append(str(root_dir))
# from api.shopping_cart import main

def get_kroger_pricing_with_id(ingredient_list, location_id):
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
                if price and item.get('inventory', {}).get('stockLevel') != "TEMPORARILY_OUT_OF_STOCK":
                    valid.append({"description": desc, "price": float(price)})
        
        if valid:
            results[ingredient] = sorted(valid, key=lambda x: x['price'])[0]
        else:
            results[ingredient] = {"description": "Not available", "price": 0.0}
    return results

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
    if pd.isna(r_string) or not isinstance(r_string, str) or r_string == "character(0)":
        return []
    content = re.sub(r'^c\(', '', r_string)
    content = re.sub(r'\)$', '', content)
    return re.findall(r'"([^"]*)"', content)

BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / "data" / "data.csv"
df = pd.read_csv(csv_path)

df['RecipeIngredientParts'] = df['RecipeIngredientParts'].apply(parse_r_list)
df['RecipeIngredientQuantities'] = df['RecipeIngredientQuantities'].apply(parse_r_list)
df['Images'] = df['Images'].apply(parse_r_list)

# --- 3. App Setup ---
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap"],
                suppress_callback_exceptions=True)

# dash.register_page(__name__, path="/")

app.layout = html.Div(style={"backgroundColor": COLORS["background"], "minHeight": "100vh", **FONT_STYLE}, children=[
    dcc.Store(id='cart-store', data={}, storage_type='session'),
    dcc.Store(id='store-id-store', data=None, storage_type='session'),
    
    # We only wrap the content area.
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
    categories = ["All"] + sorted(df['RecipeCategory'].dropna().unique().tolist())
    return dbc.Container([
        # --- Store Selection Modal ---
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Select Your Kroger Store")),
            dbc.ModalBody(id="store-selector-body"), # This will be filled with store buttons
        ], id="store-modal", is_open=False, size="lg"),

        dbc.Row([
            dbc.Col([
                html.H1("✨ Cooking Helper", style={"color": COLORS["primary"], "fontWeight": "600", "marginTop": "30px"}),
                html.P("Find recipes and check real-time Kroger prices", className="text-muted"),
            ], width=9),
            dbc.Col(dbc.Button("🛒 My Cart", href="/cart", style={"backgroundColor": COLORS["secondary"], "border": "none", "borderRadius": "20px", "marginTop": "40px"}), width=3)

        ]),
        dbc.Row([
            dbc.Col([
                html.Div(style={"backgroundColor": COLORS["white"], "padding": "20px", "borderRadius": "20px", "boxShadow": "0 4px 6px rgba(0,0,0,0.05)"}, children=[
                    html.H5("Filter"),
                    dbc.Input(id="search-query", placeholder="Search ingredients...", style={"borderRadius": "10px"}),
                    dcc.Dropdown(id="category-dropdown", options=categories, value="All", className="mt-3"),
                    
                    # --- NEW: Zip Code Search ---
                    html.Hr(),
                    html.H6("📍 Store Location", className="mt-3"),
                    dbc.Input(id="zip-input", placeholder="Enter Zip Code", type="number", style={"borderRadius": "10px"}),
                    dbc.Button("Find Stores", id="find-stores-btn", color="info", size="sm", className="mt-2 w-100", style={"borderRadius": "10px"}),
                    html.Div(id="selected-store-display", className="mt-2 small text-success", style={"fontWeight": "bold"}),
                    
                    html.Div(id="recipe-count", className="mt-2 text-muted", style={"fontSize": "0.8rem"})
                ])
            ], width=3),
            dbc.Col(html.Div(id="recipe-display-area"), width=9)
        ])
    ])

def shopping_cart_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Button("← Home", href="/", color="link", style={"color": COLORS["primary"], "marginTop": "30px", "textDecoration": "none"}), width=2),
            dbc.Col(html.H1("🌸 Your Shopping List", style={"color": COLORS["primary"], "marginTop": "30px"}), width=7),

            dbc.Col(dbc.Button("🗑️ Clear Cart", id="clear-cart-btn", color="danger", outline=True, 
                               style={"borderRadius": "20px", "marginTop": "40px", "fontSize": "0.8rem"}), width=3)
        ]),
        dbc.Row([
            dbc.Col(id="cart-container", width={"size": 10, "offset": 1}, 
                    style={"backgroundColor": COLORS["white"], "padding": "30px", "borderRadius": "30px", "marginTop": "20px", "boxShadow": "0 4px 15px rgba(0,0,0,0.05)"})
        ])
    ])

# --- 5. Callbacks ---

@callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/cart': return shopping_cart_layout()
    return recipe_finder_layout()

@callback(
    Output("recipe-display-area", "children"),
    Output("recipe-count", "children"),
    Input("search-query", "value"),
    Input("category-dropdown", "value")
)
def update_recipes(search, cat):
    filt = df.head(30).copy() 
    if cat and cat != "All": filt = filt[filt['RecipeCategory'] == cat]
    if search: filt = filt[filt['Name'].str.contains(search, case=False) | filt['RecipeIngredientParts'].astype(str).str.contains(search, case=False)]
    
    cards = []
    for idx, row in filt.iterrows():
        # Clean ingredients/quantities 
        ing_items = []
        for q, p in zip(row['RecipeIngredientQuantities'], row['RecipeIngredientParts']):
            q_str = str(q).strip() if pd.notna(q) and str(q).lower() != 'nan' else ""
            ing_items.append(html.Li(f"{q_str} {p}" if q_str else p, style={"fontSize": "0.85rem"}))

        # Servings & Image logic
        servings = html.Span(f" 🍽️ {int(row['RecipeServings'])} servings", style={"fontSize": "0.8rem", "color": COLORS["secondary"]}) if pd.notna(row['RecipeServings']) else None
        image_urls = row['Images']
        col_width, image_col = (4, dbc.Col([html.Img(src=image_urls[0], style={"width": "100%", "borderRadius": "15px"})], width=4)) if image_urls else (6, None)

        cards.append(html.Div(style={"backgroundColor": COLORS["white"], "borderRadius": "25px", "padding": "20px", "marginBottom": "25px", "boxShadow": "0 4px 15px rgba(0,0,0,0.05)"}, children=[
            html.H4(row['Name'], style={"color": COLORS["text"], "fontWeight": "600"}),
            dbc.Row([
                dbc.Col([html.H6("Ingredients", style={"color": COLORS["primary"]}), html.Ul(ing_items[:10])], width=col_width),
                dbc.Col([html.H6("About", style={"color": COLORS["primary"]}), servings, html.P(row['Description'], style={"fontSize": "0.8rem", "marginTop": "5px"})], width=col_width),
                image_col
            ]),
            dbc.Button("✨ Calculate Price", id={'type': 'add-btn', 'index': idx}, style={"backgroundColor": COLORS["primary"], "border": "none", "borderRadius": "15px", "marginTop": "10px"})
        ]))
    return cards, f"Found {len(filt)} recipes"

# 1. Search for stores and open Modal
@callback(
    Output("store-modal", "is_open"),
    Output("store-selector-body", "children"),
    Input("find-stores-btn", "n_clicks"),
    State("zip-input", "value"),
    prevent_initial_call=True
)
def find_stores(n_clicks, zip_code):
    if not zip_code: return False, ""
    
    storeLocator = KrogerStoreLocator(zip_code)
    store_locations = storeLocator.get_stores()
    # kroger = KrogerAPI()
    # kroger.authorization.get_token_with_client_credentials("product.compact")
    # locations = kroger.location.search_locations(zip_code=zip_code, radius_in_miles=10, limit=5)
    
    # print(store_locations)
    store_options = []
    for store in store_locations:
        store_options.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6(f"{store['chain'].capitalize()} - {store['name']}"),
                    html.P(store['address'], className="small text-muted"),
                    dbc.Button("Select This Store", id={'type': 'select-store-btn', 'id': store['location_id'], 'name': store['name']}, color="primary", size="sm")
                ])
            ], className="mb-2")
        )
    
    return True, store_options


# 2. Save the selected store ID to dcc.Store
@callback(
    Output("store-id-store", "data"),
    Output("store-modal", "is_open", allow_duplicate=True),
    Output("selected-store-display", "children"),
    Input({'type': 'select-store-btn', 'id': ALL, 'name': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def save_store(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks): return dash.no_update, dash.no_update, dash.no_update
    
    # Get the ID and Name from the button that was clicked
    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    selected_id = button_id['id']
    selected_name = button_id['name']
    
    return selected_id, False, f"📍 {selected_name}"

@callback(
    Output('cart-store', 'data', allow_duplicate=True),
    Output('url', 'pathname'),
    Input({'type': 'add-btn', 'index': ALL}, 'n_clicks'),
    State('cart-store', 'data'),
    State('store-id-store', 'data'), # Access the saved Store ID
    prevent_initial_call=True
)
def add_to_cart(n_clicks, cart, store_id):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks): return cart, dash.no_update
    
    # Fallback to a default ID if they haven't picked one yet
    loc_id = store_id if store_id else "01400394" 
    
    idx = eval(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    ingredients = df.iloc[idx]['RecipeIngredientParts']
    
    # get_kroger_pricing to accept the location_id directly
    shopping_cart = ShoppingCart(loc_id)
    print(ingredients)
    ingredients_list = shopping_cart.price_ingredients(ingredients)
    real_prices = shopping_cart.get_cheapest_ingredients(ingredients_list)
    # real_prices = get_kroger_pricing_with_id(ingredients, loc_id)
    
    cart = {} # Reset cart
    for ing, data in real_prices.items():
        if ing not in cart:
            cart[ing] = {"description": data['description'], "price": data['price'], "qty": 1}
        else:
            cart[ing]["qty"] += 1
            
    return cart, '/cart'

@callback(
    Output('cart-store', 'data', allow_duplicate=True),
    Input('clear-cart-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_cart(n_clicks):
    if n_clicks:
        return {} 
    return dash.no_update

# INTERACTIVE CART logic
@callback(
    Output('cart-store', 'data'),
    Input({'type': 'cart-item-btn', 'action': ALL, 'item': ALL}, 'n_clicks'),
    State('cart-store', 'data'),
    prevent_initial_call=True
)
def update_cart_quantities(n_clicks, cart):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks): return cart
    btn_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    action, item_key = btn_id['action'], btn_id['item']
    
    if item_key in cart:
        if action == 'plus': cart[item_key]['qty'] += 1
        elif action == 'minus':
            if cart[item_key]['qty'] > 1: cart[item_key]['qty'] -= 1
            else: del cart[item_key]
        elif action == 'delete': del cart[item_key]
    return cart

# RENDER CART logic
@callback(
    Output('cart-container', 'children'),
    Input('cart-store', 'data')
)
def render_cart(cart):
    if not cart: return html.Div("Your basket is empty! ✨", className="text-center mt-5")
    
    table_rows, grand_total = [], 0
    for item, info in cart.items():
        # SAFETY CHECK: If info is not a dictionary (old data), skip it or fix it
        if not isinstance(info, dict): continue
        
        desc = info.get('description', 'Kroger Item')
        price = info.get('price', 0.0)
        qty = info.get('qty', 1)
        subtotal = qty * price
        grand_total += subtotal
        
        table_rows.append(html.Tr([
            html.Td([html.B(item), html.Br(), html.Small(desc, className="text-muted")]),
            html.Td([
                dbc.ButtonGroup([
                    dbc.Button("-", id={'type': 'cart-item-btn', 'action': 'minus', 'item': item}, size="sm", color="light"),
                    html.Span(f" {qty} ", className="mx-3", style={"lineHeight": "31px"}),
                    dbc.Button("+", id={'type': 'cart-item-btn', 'action': 'plus', 'item': item}, size="sm", color="light"),
                ])
            ], style={"textAlign": "center"}),
            html.Td(f"${price:.2f}", style={"textAlign": "right"}),
            html.Td(f"${subtotal:.2f}", style={"textAlign": "right", "fontWeight": "600"}),
            html.Td(dbc.Button("×", id={'type': 'cart-item-btn', 'action': 'delete', 'item': item}, color="light", size="sm", style={"borderRadius": "50%"}))
        ]))
    
    table_rows.append(html.Tr([
        html.Td("Grand Total", colSpan=3, style={"fontWeight": "600", "color": COLORS["primary"], "fontSize": "1.2rem"}),
        html.Td(f"${grand_total:.2f}", style={"fontWeight": "700", "color": COLORS["primary"], "fontSize": "1.2rem", "textAlign": "right"}),
        html.Td("")
    ]))
    
    return dbc.Table([
        html.Thead(html.Tr([html.Th("Item"), html.Th("Qty", className="text-center"), html.Th("Price", className="text-end"), html.Th("Subtotal", className="text-end"), html.Th("")])),
        html.Tbody(table_rows)
    ], borderless=True, hover=True)

if __name__ == "__main__":
    app.run(debug=True)