# Component Specification

## Component 1: Recipe Data Manager

### Description
Manages access to the curated recipe dataset and provides search and filtering functionality.

### Inputs
- search_query: string
- filters: dictionary (e.g., cuisine type)

### Outputs
- List of Recipe objects:
  - id: int
  - name: string
  - ingredients: list of strings
  - instructions: string
  - cuisine: string

### Responsibilities
- Load curated dataset
- Perform keyword search
- Apply cuisine filters
- Return structured recipe objects


---

## Component 2: Location & Store Service

### Description
Handles store lookup functionality using the Kroger API.

### Inputs
- zipcode: string

### Outputs
- store_id: string

### Responsibilities
- Validate zipcode
- Authenticate with Kroger API
- Retrieve nearest store ID
- Handle API errors


---

## Component 3: Cart & Pricing Manager

### Description
Generates a shopping cart based on recipe ingredients and retrieves pricing information from Kroger API.

### Inputs
- recipe_id: int
- store_id: string

### Outputs
- List of CartItem objects:
  - name: string
  - price: float
  - quantity: string
- total_cost: float

### Responsibilities
- Retrieve ingredient list from Recipe Data Manager
- Query Kroger API for pricing data
- Select lowest available priced item
- Compile structured shopping cart
- Recalculate total when items are removed


---

## Component 4: Frontend Controller

### Description
Handles user interactions and coordinates communication between components.

### Inputs
- User search input
- Zip code input
- Recipe selection
- Ingredient removal selection

### Outputs
- Rendered recipe list
- Displayed shopping cart
- Displayed instructions

### Responsibilities
- Collect user input
- Call appropriate backend components
- Display formatted results
