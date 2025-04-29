from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime

def create_date_filters():
    current_year = datetime.now().year
    return dbc.Row([
        dbc.Col([
            html.Label("Ano"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(i), 'value': i} for i in range(2020, current_year + 1)],
                value=current_year
            )
        ], width=2),
        dbc.Col([
            html.Label("Mês"),
            dcc.Dropdown(
                id='month-dropdown',
                options=[
                    {'label': 'Janeiro', 'value': 1},
                    {'label': 'Fevereiro', 'value': 2},
                    {'label': 'Março', 'value': 3},
                    {'label': 'Abril', 'value': 4},
                    {'label': 'Maio', 'value': 5},
                    {'label': 'Junho', 'value': 6},
                    {'label': 'Julho', 'value': 7},
                    {'label': 'Agosto', 'value': 8},
                    {'label': 'Setembro', 'value': 9},
                    {'label': 'Outubro', 'value': 10},
                    {'label': 'Novembro', 'value': 11},
                    {'label': 'Dezembro', 'value': 12}
                ],
                value=datetime.now().month
            )
        ], width=2)
    ])