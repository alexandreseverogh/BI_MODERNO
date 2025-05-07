import dash
import dash_bootstrap_components as dbc
import time

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        dbc_css,
        {'href': '/assets/css/style.css?v=' + str(int(time.time()))}
    ],
    suppress_callback_exceptions=True
)

server = app.server