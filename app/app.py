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

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
from api.shopping_cart import main

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
        
    if valid_options:
        # Sort by price and pick cheapest 
        ingredient_results[ingredient] = sorted(valid_options, key=lambda x: x['price'])[0]
            
    return ingredient_results

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
    
    # This finds all text inside quotes
    parts = re.findall(r'"([^"]*)"', content)
    
    # Removes any steps that are just commas, spaces, or empty
    parts = [p.strip() for p in parts if p.strip() and p.strip() != ","]
    parts = [p.replace('\\', '').strip() for p in parts if p.strip() and p.strip() != ","]
    if not parts and content.strip():
        return [content.strip()]
        
    return parts

BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / "data" / "data.csv"
df = pd.read_csv(csv_path)

df['RecipeIngredientParts'] = df['RecipeIngredientParts'].apply(parse_r_list)
df['RecipeIngredientQuantities'] = df['RecipeIngredientQuantities'].apply(parse_r_list)
df['Images'] = df['Images'].apply(parse_r_list)
df['RecipeInstructions'] = df['RecipeInstructions'].apply(parse_r_list)

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
            dbc.ModalBody(id="store-selector-body"),
        ], id="store-modal", is_open=False, size="lg"),

        # --- Store Warning Toast ---
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
                html.H1("✨ Cooking Helper", style={"color": COLORS["primary"], "fontWeight": "600", "marginTop": "30px"}),
                html.P("Find recipes and check real-time Kroger prices", className="text-muted"),
            ], width=9),
            dbc.Col(dbc.Button("🛒 My Cart", href="/cart", style={"backgroundColor": COLORS["secondary"], "border": "none", "borderRadius": "20px", "marginTop": "40px"}), width=3)

        ]),

        dbc.Row([
            # --- Sidebar Column ---
            # --- Sidebar Column ---
            dbc.Col([
                html.Div(style={"backgroundColor": COLORS["white"], "padding": "20px", "borderRadius": "20px", "boxShadow": "0 4px 6px rgba(0,0,0,0.05)"}, children=[
                    
                    # --- 📍 STORE LOCATION SECTION ---
                    html.H5("📍 Store Location", style={"color": COLORS["text"]}),
                    
                    # This container holds the input. We hide/show it via CSS.
                    html.Div(id="zip-container", children=[
                        dbc.Input(id="zip-input", placeholder="Enter Zip Code", type="number", style={"borderRadius": "10px"}, className="mt-2"),
                        dbc.Button("Find Stores", id="find-stores-btn", color="info", size="sm", className="mt-2 w-100", 
                                   style={"borderRadius": "10px", "backgroundColor": COLORS["secondary"], "border": "none"}),
                    ]),
                    
                    # This container holds the "Change" button and the selected name.
                    html.Div(id="change-loc-container", style={"display": "none"}, children=[
                        dbc.Button("🔄 Change Location", id="change-loc-btn", color="secondary", outline=True, size="sm", className="mt-2 w-100", 
                                   style={"borderRadius": "10px"}),
                        html.Div(id="selected-store-display", className="mt-2 small text-success", style={"fontWeight": "bold"}),
                    ]),
                    
                    html.Hr(className="my-4"), 

                    # --- 🔍 FILTER SECTION ---
                    html.H5("Filter Recipes", style={"color": COLORS["text"]}),
                    dbc.Input(id="search-query", placeholder="Search ingredients...", style={"borderRadius": "10px"}, className="mt-2"),
                    dcc.Dropdown(id="category-dropdown", options=categories, value="All", className="mt-3", style={"borderRadius": "10px"}),
                    html.Div(id="recipe-count", className="mt-3 text-muted", style={"fontSize": "0.8rem"})
                ])
            ], width=3),
            
            # --- Recipe Display Area ---
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

@callback(
    Output("zip-container", "style"),
    Output("change-loc-container", "style"),
    Output("store-id-store", "data", allow_duplicate=True), 
    Input("change-loc-btn", "n_clicks"),
    Input("store-id-store", "data"),
    prevent_initial_call=True
)
def manage_location_ui(change_clicks, store_id):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # CASE 1: User wants to change location
    if triggered_id == "change-loc-btn":
        # Show input, Hide change button, Clear store data
        return {"display": "block"}, {"display": "none"}, None
    
    # CASE 2: A store has been selected (store_id is updated)
    if store_id:
        # Hide input, Show change button
        return {"display": "none"}, {"display": "block"}, dash.no_update

    # Default State
    return {"display": "block"}, {"display": "none"}, dash.no_update

def toggle_location_button(store_id):
    if not store_id:
        # Initial State: Show zip input, blue button
        return {"display": "block"}, "Find Stores", "info", False
    
    # Selected State: Hide zip input, turn button into "Change Location"
    return {"display": "none"}, "🔄 Change Location", "secondary", True
    

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
    State("zip-input", "value"), # This ID must always exist in the layout!
    prevent_initial_call=True
)
def find_stores(n_clicks, zip_code):
    # If the user clicked "Change Location", zip_code will still 
    # hold the last value entered.
    if not zip_code:
        return True, "Please enter a zip code first."
    
    storeLocator = KrogerStoreLocator(zip_code)
    store_locations = storeLocator.get_stores()
    # kroger = KrogerAPI()
    # kroger.authorization.get_token_with_client_credentials("product.compact")
    # locations = kroger.location.search_locations(zip_code=zip_code, radius_in_miles=10, limit=5)
    kroger = KrogerAPI()
    kroger.authorization.get_token_with_client_credentials("product.compact")
    
    # Radius set to 10 miles as per your current logic
    locations = kroger.location.search_locations(zip_code=zip_code, radius_in_miles=10, limit=5)
    
    # --- CHECK IF STORES EXIST ---
    if not locations.get("data") or len(locations["data"]) == 0:
        return True, html.Div([
            html.P("Your zip code does not have any Kroger stores close to you. Please enter a different zip code!", 
                   style={"color": "red", "fontWeight": "bold", "textAlign": "center"})
        ])
    
    # --- IF STORES EXIST, CREATE CARDS ---
    store_options = []
    for store in store_locations:
        store_options.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6(f"{store['chain'].capitalize()} - {store['name']}"),
                    html.P(store['address'], className="small text-muted"),
                    dbc.Button("Select This Store", id={'type': 'select-store-btn', 'id': store['location_id'], 'name': store['name']}, color="primary", size="sm")
                    html.H6(f"{loc['chain'].capitalize()} - {loc['name']}"),
                    html.P(full_addr, className="small text-muted"),
                    dbc.Button("Select This Store", 
                               id={'type': 'select-store-btn', 'id': loc['locationId'], 'name': loc['name']}, 
                               color="primary", size="sm")
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
    Output('url', 'pathname', allow_duplicate=True),
    Output('store-warning-toast', 'is_open'),
    Input({'type': 'add-btn', 'index': ALL}, 'n_clicks'),
    State('cart-store', 'data'),
    State('store-id-store', 'data'),
    prevent_initial_call=True
)
def add_to_cart(n_clicks, cart_data, store_id):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks): 
        # Return: cart_data, no_update (url), False (toast)
        return cart_data, dash.no_update, False
    
    # 1. CHECK FOR STORE SELECTION
    if not store_id:
        # Return: cart_data, no_update (url), True (SHOW TOAST)
        return cart_data, dash.no_update, True

    # 2. INITIALIZE DATA STRUCTURE
    if not cart_data or 'items' not in cart_data:
        cart_data = {'items': {}, 'recipes': []}

    # 3. IDENTIFY RECIPE
    idx = eval(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    ingredients = df.iloc[idx]['RecipeIngredientParts']
    
    # get_kroger_pricing to accept the location_id directly
    shopping_cart = ShoppingCart(loc_id)
    print(ingredients)
    ingredients_list = shopping_cart.price_ingredients(ingredients)
    real_prices = shopping_cart.get_cheapest_ingredients(ingredients_list)
    # real_prices = get_kroger_pricing_with_id(ingredients, loc_id)
    recipe_row = df.iloc[idx]
    
    # 4. SAVE RECIPE DETAILS
    recipe_info = {
        "name": recipe_row['Name'],
        "ingredients": list(zip(recipe_row['RecipeIngredientQuantities'], recipe_row['RecipeIngredientParts'])),
        "instructions": recipe_row['RecipeInstructions']
    }
    
    # Avoid duplicates
    if recipe_info['name'] not in [r['name'] for r in cart_data['recipes']]:
        cart_data['recipes'].append(recipe_info)

    # 5. FETCH KROGER PRICING
    # We already checked store_id exists above, so we use it here
    real_prices = get_kroger_pricing_with_id(recipe_row['RecipeIngredientParts'], store_id)
    
    cart = {} # Reset cart
    for ing, data in real_prices.items():
        if ing not in cart_data['items']:
            cart_data['items'][ing] = {"description": data['description'], "price": data['price'], "qty": 1}
        else:
            cart_data['items'][ing]["qty"] += 1
            
    # 6. FINAL RETURN (Success)
    # Return: updated cart, redirect to cart page, False (hide/keep toast closed)
    return cart_data, '/cart', False

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
    
    # Target the 'items' sub-dictionary
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

# RENDER CART logic
@callback(
    Output('cart-container', 'children'),
    Input('cart-store', 'data')
)
def render_cart(cart_data):
    if not cart_data or not cart_data.get('items'): 
        return html.Div("Your basket is empty! ✨", className="text-center mt-5")
    
    # --- Part A: Recipe Reference Section ---
    recipe_sections = []
    for recipe in cart_data.get('recipes', []):
        recipe_sections.append(html.Div(style={"marginBottom": "30px", "borderBottom": f"1px solid {COLORS['background']}", "paddingBottom": "20px"}, children=[
            html.H3(f"📖 {recipe['name']}", style={"color": COLORS["text"]}),
            dbc.Row([
                dbc.Col([
                    html.H6("Original Ingredients", style={"color": COLORS["primary"]}),
                    html.Ul([html.Li(f"{q} {i}", style={"fontSize": "0.85rem"}) for q, i in recipe['ingredients']])
                ], width=4),
                dbc.Col([
                    html.H6("Instructions", style={"color": COLORS["primary"]}),
                    html.Ol([html.Li(step, style={"fontSize": "0.85rem", "marginBottom": "5px"}) for step in recipe['instructions']])
                ], width=8)
            ])
        ]))

    # --- Part B: Pricing Table ---
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

    pricing_table = dbc.Table([
        html.Thead(html.Tr([html.Th("Item"), html.Th("Qty", className="text-center"), html.Th("Price", className="text-end"), html.Th("Subtotal", className="text-end"), html.Th("")])),
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