Adam is a college student.
Adam wants to eat healthier and save more money.
Adam wants to eat out less.
Adam wants to easily figure out what ingredients he needs.
Adam wants does not have high technical skills and values a simple interface to make things as easy as possible.

Sarah is a young working adult.
Sarah feels overwhelmed at the grocery store.
Sarah often overbuys at the grocery store.
Sarah works long hours and has very little time to spend at the store.
Sarah has some technical skills but wants a quick answer.

User Case:
Objective: System displays accurate search results that user needs
User: Search for recipe by entering word or scrolling through page
System: Queries results from search or shows all recipe while scrolling
User: Filter by cuisine
System: Show subset of item

User Case
Objective: System processes recipe user has selected
User: Selects Recipe
System: Prompts user to enter zip code
User: Inputs zip code
System: Queries the API and takes given recipe ingredients and location to get "shopping cart".

User Case
Objective: System displays accurately updates shopping cart.
User: Selects ingredients they already have.
System: Removes selected ingredients from shopping cart and updates price.

Component Design:

Name: searchRecipe
What it does: Returns recipes that match description
Inputs: recipe name or filter selection
Outputs: list of recipes with descriptions if possible
Assumptions: none

title search recipe

user->System: text based string input or filter selection
System -> Database: if it's text, query by recipe name, if filter, shows recipes
Database -> System: compiles results of user input, are there results or not
System -> User: return results to user

Name: inputLocation
What it does: Locate store for user
Input: Zip code, City, State
Output: Store closest to them (not explicity shown to user)
Assumption: User is near a Kroger/wants to go to Kroger

title Store Location
user -> system: zip code
API Call: obtain store id 

Name: createCart
What it does: Gather ingredients for user
Input: Recipe Name, storeid
Output: list of ingredients from given Kroger store and price
Assumption: they want the cheapest item.

title create cart 
system -> database: get recipe ingredients
database -> API: get ingredients and price points
API -> System: put everything in cart
System -> output list of items in cart


Name: showRecipe
What it does: Display the recipe and instructions and shopping cart
Input: createCart
Output: Display the recipe and instructions and shopping cart
Assumption: They still want the recipe.

title showRecipe
Database to system: get the instructions of recipe
System -> user: output of shopping cart and instructions on to a page





