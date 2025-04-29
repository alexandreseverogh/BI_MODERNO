import dash
import dash_bootstrap_components as dbc
import time

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        {'href': '/assets/css/style.css?v=' + str(int(time.time()))}
    ],
    suppress_callback_exceptions=True
)

server = app.server