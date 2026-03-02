import pandas as pd
import re
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# print(BASE_DIR)
csv_path = BASE_DIR / "data" / "data.csv"
# print(csv_path)


# --- 1. Data Processing (Same Logic) ---
def parse_r_list(r_string):
    if pd.isna(r_string) or not isinstance(r_string, str):
        return []
    content = re.sub(r'^c\(', '', r_string)
    content = re.sub(r'\)$', '', content)
    return re.findall(r'"([^"]*)"', content)


df = pd.read_csv(csv_path)
df['RecipeIngredientParts'] = df['RecipeIngredientParts'].apply(parse_r_list)
df['RecipeIngredientQuantities'] = df['RecipeIngredientQuantities'].apply(parse_r_list)
df['RecipeInstructions'] = df['RecipeInstructions'].apply(parse_r_list)

categories = ["All"] + sorted(df['RecipeCategory'].dropna().unique().tolist())

# --- 2. App Layout ---
dash.register_page(__name__, path="/")

layout = dbc.Container([
    dbc.Row([
        html.H1("🍳 Cooking Helper: Recipe Finder", className="text-center my-4"),
        html.Hr()
    ]),
    
    dbc.Row([
        # Sidebar/Filters Column
        dbc.Col([
            html.H4("Filter Recipes"),
            html.Label("Search Name or Ingredient:"),
            dbc.Input(id="search-query", placeholder="Search...", type="text"),
            
            html.Br(),
            html.Label("Category:"),
            dcc.Dropdown(id="category-dropdown", options=categories, value="All"),
            
            html.Div(id="recipe-count", className="mt-3 text-muted")
        ], width=3),
        
        # Main Display Column
        dbc.Col([
            html.Div(id="recipe-display-area")
        ], width=9)
    ])
], fluid=True)

# --- 3. Callbacks (The Search Logic) ---
@callback(
    Output("recipe-display-area", "children"),
    Output("recipe-count", "children"),
    Input("search-query", "value"),
    Input("category-dropdown", "value")
)
def update_recipes(search_query, selected_category):
    filtered_df = df.copy()

    # Apply Category Filter
    if selected_category and selected_category != "All":
        filtered_df = filtered_df[filtered_df['RecipeCategory'] == selected_category]

    # Apply Search Filter
    if search_query:
        mask = (
            filtered_df['Name'].str.contains(search_query, case=False, na=False) |
            filtered_df['RecipeIngredientParts'].astype(str).str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    # Build the UI Components
    recipe_cards = []
    for index, row in filtered_df.iterrows():
        # Build Ingredient List
        ingredients = [html.Li(f"{qty} {part}") for qty, part in zip(row['RecipeIngredientQuantities'], row['RecipeIngredientParts'])]
        
        # Build Instructions List
        instructions = [html.P(f"{i+1}. {step}") for i, step in enumerate(row['RecipeInstructions'])]

        # Create an Accordion item (Equivalent to Streamlit Expander)
        card = dbc.Accordion(
            dbc.AccordionItem([
                dbc.Row([
                    dbc.Col([
                        html.H5("🛒 Ingredients"),
                        html.Ul(ingredients),
                        dcc.Link(
                            dbc.Button("Calculate Price", color="info", size="sm"),
                            href=f"/recipes/{row['RecipeId']}"
                        )
                    ], width=4),
                    dbc.Col([
                        html.H5("📝 Instructions"),
                        html.Div(instructions)
                    ], width=8)
                ])
            ], title=f"{row['Name']} ({row['RecipeCategory']})"),
            start_collapsed=True,
            className="mb-2"
        )
        recipe_cards.append(card)

    count_text = f"Showing {len(filtered_df)} recipes."
    return recipe_cards, count_text

# if __name__ == "__main__":
#     print("--- Dash is starting up! ---")
#     app.run(debug=True)
