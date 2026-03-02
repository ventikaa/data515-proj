import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
from api.kroger_auth import init_kroger_env
init_kroger_env()

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = dbc.Container([
    # html.H1("🍳 Cooking Recipe App", className="text-center my-4"),

    # # Navigation links (optional but recommended)
    # dbc.Nav(
    #     [
    #         dbc.NavLink("Home", href="/", active="exact"),
    #     ],
    #     pills=True,
    #     className="mb-4"
    # ),

    # This is where pages render
    dash.page_container
], fluid=True)

if __name__ == "__main__":
    # print(dash.page_registry)

    app.run(debug=True)