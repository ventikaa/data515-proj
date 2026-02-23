import streamlit as st
import pandas as pd
import re

# Page Configuration
st.set_page_config(page_title="Cooking Helper! 🧑‍🍳", layout="wide")

# Helper function to convert R-style strings c("a", "b") to Python lists
def parse_r_list(r_string):
    if pd.isna(r_string) or not isinstance(r_string, str):
        return []
    content = re.sub(r'^c\(', '', r_string)
    content = re.sub(r'\)$', '', content)
    return re.findall(r'""(.*?)""', content)

# 2. Optimized Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv') 
    df['RecipeIngredientParts'] = df['RecipeIngredientParts'].apply(parse_r_list)
    df['RecipeIngredientQuantities'] = df['RecipeIngredientQuantities'].apply(parse_r_list)
    df['RecipeInstructions'] = df['RecipeInstructions'].apply(parse_r_list)
    return df

df = load_data()

# 3. Sidebar Filters
st.sidebar.header("Filter Recipes")
search_query = st.sidebar.text_input("Search by Name or Ingredient", "")

categories = ["All"] + sorted(df['RecipeCategory'].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

# 4. Search Logic
filtered_df = df.copy()

if search_query:
    # Search in Name and the cleaned Ingredient Parts list
    filtered_df = filtered_df[
        filtered_df['Name'].str.contains(search_query, case=False, na=False) |
        filtered_df['RecipeIngredientParts'].astype(str).str.contains(search_query, case=False, na=False)
    ]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df['RecipeCategory'] == selected_category]

# 5. Main UI Display
st.title("🍳 Cooking Helper: Recipe Finder")
st.write(f"Showing {len(filtered_df)} recipes from your collection.")

# Create the display loop
for index, row in filtered_df.iterrows():
    # Expanders keep the UI clean
    with st.expander(f"{row['Name']} ({row['RecipeCategory']})"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("🛒 Ingredients")
            # Loop through both quantity and part lists together
            for qty, part in zip(row['RecipeIngredientQuantities'], row['RecipeIngredientParts']):
                st.write(f"- **{qty}** {part}")
            
            # Button placeholder for your Kroger API Logic
            if st.button(f"Calculate Price", key=f"btn_{index}"):
                st.info(f"Connecting to Kroger API for {len(row['RecipeIngredientParts'])} items...")
        
        with col2:
            st.subheader("📝 Instructions")
            for i, step in enumerate(row['RecipeInstructions'], 1):
                st.write(f"**{i}.** {step}")