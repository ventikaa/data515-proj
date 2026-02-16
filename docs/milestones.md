# Milestones

## Milestone 1: Data Curation (Highest Priority)

Goal: Prepare a clean and structured recipe dataset for system querying.

Tasks (in priority order):
1. Clean Kaggle recipe dataset.
2. Remove incomplete recipes (missing ingredients or instructions).
3. Standardize ingredient naming.
4. Trim dataset to 100–200 curated recipes.
5. Save cleaned dataset in structured format (JSON or CSV).

Deliverable:
- Cleaned dataset file
- Documented data schema

Dependency:
Required before backend querying and cart generation.


## Milestone 2: Backend Recipe Query System

Goal: Enable recipe search and filtering functionality.

Tasks:
1. Implement search by recipe name.
2. Implement filtering by cuisine.
3. Define Recipe object structure.
4. Add unit tests for search functionality.

Deliverable:
- Working recipe query module
- Basic test coverage


## Milestone 3: Location API Integration

Goal: Retrieve nearest Kroger store based on user zip code.

Tasks:
1. Implement Kroger API authentication.
2. Build store lookup function.
3. Parse store ID from API response.
4. Handle invalid zip code errors.

Deliverable:
- Working store lookup function
- Example API call demonstration


## Milestone 4: Shopping Cart & Pricing Integration

Goal: Generate ingredient pricing cart for selected recipe.

Tasks:
1. Extract ingredient list from selected recipe.
2. Query Kroger API for product pricing.
3. Select lowest priced available items.
4. Compute total cost.
5. Enable ingredient removal and price update.

Deliverable:
- Functional shopping cart module
- Pricing breakdown display


## Milestone 5: Front-End Interface

Goal: Provide a user interface for interaction.

Tasks:
1. Implement recipe search page.
2. Implement zip code input.
3. Display recipe details and instructions.
4. Display shopping cart and total cost.
5. Support ingredient removal interaction.

Deliverable:
- Functional UI prototype
- End-to-end demo
