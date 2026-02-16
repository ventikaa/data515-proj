
**Component Design:**

**Name: searchRecipe**

What it does: Returns recipes that match description

Inputs: recipe name or filter selection

Outputs: list of recipes with descriptions if possible

Assumptions: none


**title search recipe**

user->System: text based string input or filter selection

System -> Database: if it's text, query by recipe name, if filter, shows recipes

Database -> System: compiles results of user input, are there results or not

System -> User: return results to user <br><br><br>


**Name: inputLocation**

What it does: Locate store for user

Input: Zip code, City, State

Output: Store closest to them (not explicity shown to user)

Assumption: User is near a Kroger/wants to go to Kroger


**title Store Location**

user -> system: zip code

API Call: obtain store id  <br><br><br>


**Name: createCart**

What it does: Gather ingredients for user

Input: Recipe Name, storeid

Output: list of ingredients from given Kroger store and price

Assumption: they want the cheapest item.


**title create cart**

system -> database: get recipe ingredients

database -> API: get ingredients and price points

API -> System: put everything in cart

System -> output list of items in cart <br><br><br>



**Name: showRecipe**

What it does: Display the recipe and instructions and shopping cart

Input: createCart

Output: Display the recipe and instructions and shopping cart

Assumption: They still want the recipe.


**title showRecipe**

Database to system: get the instructions of recipe

System -> user: output of shopping cart and instructions on to a page

The diagrams are illustrated in the Component_Diagram.png file within the docs/ folder





