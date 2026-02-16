## Background

Cooking Aide is a tool project designed to help users efficiently select recipes and generate a cost-aware grocery shopping cart based on their location. Many students and working professionals struggle with meal planning, budgeting, and navigating grocery store inventory. Users often overbuy ingredients, waste food, or feel overwhelmed by pricing decisions.

Cooking Aide integrates a curated recipe dataset with real-time pricing and store data from the Kroger API. By combining these two data sources, the system allows users to move seamlessly from discovering a recipe to generating a location-specific shopping cart with estimated prices.

The goal of this system is to simplify meal planning, reduce grocery costs, and improve shopping efficiency.


## User Profiles

### User Profile 1: Adam (College Student)

- Limited budget
- Minimal technical skills
- Wants to eat healthier
- Wants to reduce eating out
- Prefers a simple and intuitive interface
- Has basic web browsing skills, no programming experience

### User Profile 2: Sarah (Working Professional)

- Limited time due to long work hours
- Feels overwhelmed at grocery stores
- Often overbuys unnecessary items
- Has moderate technical familiarity
- Wants fast and clear results


## Data Sources

### Data Source 1: Kaggle Recipe Dataset

This dataset contains structured recipe information including:
- Recipe name
- Ingredients list
- Instructions
- Cuisine or category labels

The dataset will be curated and cleaned to a subset of approximately 100–200 recipes to ensure consistency and structured formatting. It will support search, filtering, and ingredient extraction.

Limitations:
- Static dataset
- No pricing data
- Ingredient naming inconsistencies


### Data Source 2: Kroger API

The Kroger API provides:
- Store lookup based on zip code
- Product availability
- Real-time pricing data

The system will use the API to:
- Retrieve the nearest store ID
- Query pricing for recipe ingredients
- Generate a shopping cart with estimated total cost

Limitations:
- API authentication required
- Rate limits
- Product matching may not be exact


## Use Cases

### Use Case 1: Search for a Recipe

**Objective:**  
User searches for a recipe by keyword or cuisine filter.

**Precondition:**  
Curated recipe dataset is loaded.

**Interaction Steps:**

1. User enters a keyword (e.g., "chicken") or selects a cuisine filter.
2. System queries the curated recipe dataset.
3. System returns a list of matching recipes.
4. User selects one recipe from the results.

**Postcondition:**  
Selected recipe ID is passed to the cart generation workflow.


### Use Case 2: Generate Shopping Cart

**Objective:**  
User generates a grocery shopping cart with location-based pricing.

**Precondition:**  
User has selected a recipe.

**Interaction Steps:**

1. System prompts user to enter a zip code.
2. User inputs zip code.
3. System calls Kroger API to retrieve nearest store ID.
4. System retrieves ingredient list from selected recipe.
5. System queries Kroger API for product pricing.
6. System compiles a structured shopping cart with item names and prices.
7. Shopping cart and total estimated cost are displayed.

**Postcondition:**  
User sees complete cart with pricing breakdown.


### Use Case 3: Update Shopping Cart

**Objective:**  
User removes ingredients they already have at home.

**Precondition:**  
Shopping cart has been generated.

**Interaction Steps:**

1. User selects ingredients they already own.
2. System removes selected ingredients from the cart.
3. System recalculates total cost.
4. Updated cart is displayed to the user.

**Postcondition:**  
User sees updated ingredient list and total cost.
