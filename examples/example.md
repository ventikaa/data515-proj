# For Collaborators -- How to Run/Deploy Our Project

The following instructions are to be performed in a command line interface from the root directory of the project:
- "git clone" the repository to download the latest version of the application
- Download conda, and creating a virtual environment from the environment.yml file, located at the root of the repository. 
    - The command for this is conda env create -f environment.yml.
- The public Kroger Developer API key is needed for this project.
    - Navigate to the [Kroger Developer Site](https://developer.kroger.com/api-products) and make an account. Request access for the location and product access. You will be allocated a Kroger Client ID and Client Secret. Add these into your .env file like below (Do not share these secrets!).
    - KROGER_CLIENT_ID=INSERT_CLIENT_ID_HERE
    - KROGER_CLIENT_SECRET=INSERT_CLIENT_SECRET_HERE
- Run "python app/app.py"

![Home Page](images/Front-Page.png)

The app will run on the URL: http://127.0.0.1:8050/

# How to Use App

- Enter your zip code
- Select your store of interest
![Select Store](images/Select-Store.png)
- Scroll through recipes or search and press enter for a specific recipe
- Click calculate price
- Add quantities of ingredients or click the x if you don't want a certain ingredient
![Shopping Cart](images/Shopping-Cart.png)
- Click clear cart if you don't want this recipe anymore
- Make your recipe!
