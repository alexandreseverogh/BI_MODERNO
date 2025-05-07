import os
import time

def update_project_files():
    base_path = r"C:\falcao\GORE"
    
    # Conteúdo dos arquivos principais
    files_content = {
        'components/navbar.py': '''
import dash_bootstrap_components as dbc
from dash import html

def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Atendimentos", href="/atendimentos")),
            dbc.NavItem(dbc.NavLink("Agendamentos", href="/agendamentos")),
            dbc.NavItem(dbc.NavLink("Convênios", href="/convenios")),
            dbc.NavItem(dbc.NavLink("Contas a Pagar", href="/contas-pagar")),
            dbc.NavItem(dbc.NavLink("Contas a Receber", href="/contas-receber")),
            dbc.NavItem(dbc.NavLink("DRE", href="/dre")),
            dbc.NavItem(dbc.NavLink("Clientes", href="/clientes")),
            dbc.NavItem(dbc.NavLink("Dados Médicos", href="/dados-medicos")),
            dbc.NavItem(dbc.NavLink("Dados Brutos", href="/dados-brutos")),
        ],
        brand="BioImagem",
        brand_href="/",
        color="dark",
        dark=True,
    )
    return navbar
''',
        'components/filters.py': '''
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
''',
        'components/cards.py': '''
from dash import html
import dash_bootstrap_components as dbc

def create_metric_card(title, value, comparison_value, variation):
    color = "success" if float(variation.replace('%', '').replace(',', '.')) > 0 else "danger"
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title"),
            html.H3(value),
            html.P([
                f"Anterior: {comparison_value}",
                html.Span(
                    f" ({variation})", 
                    style={'color': 'green' if color == "success" else 'red'}
                )
            ])
        ]),
        className="mb-4"
    )
''',
        'layouts/atendimentos.py': '''
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.filters import create_date_filters
from components.cards import create_metric_card

def create_layout():
    return html.Div([
        dbc.Container([
            html.H1("Dashboard de Atendimentos", className="my-4"),
            create_date_filters(),
            html.Div(id='metrics-container'),
            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Evolução de Atendimentos", className="card-title"),
                            dcc.Graph(id='atendimentos-graph')
                        ])
                    ),
                    width=12
                )
            ], className="mt-4")
        ])
    ])
''',
        'callbacks/atendimentos_callbacks.py': '''
from dash.dependencies import Input, Output
from app import app
import pandas as pd
import psycopg2
from datetime import datetime
from components.cards import create_metric_card
import dash_bootstrap_components as dbc

def get_db_connection():
    return psycopg2.connect(
        dbname='BI_GORE',
        user='postgres',
        password='postgre123',
        host='localhost'
    )

@app.callback(
    Output('metrics-container', 'children'),
    [Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_metrics(year, month):
    start = time.time()
    print('[PERF] Callback: update_metrics - INÍCIO')
    try:
        conn = get_db_connection()
        # Implementar as queries necessárias aqui
        return dbc.Row([
            dbc.Col(create_metric_card(
                "Qtde Acum Mês do Ano Atual",
                "1.093",
                "1.365",
                "-19,93%"
            ), width=4),
            dbc.Col(create_metric_card(
                "Qtde Méd Diária Mês do Ano Atual",
                "64",
                "59",
                "8,33%"
            ), width=4),
            dbc.Col(create_metric_card(
                "Proj Qtde p/ Mês do Ano Atual",
                "1.543",
                "1.365",
                "13,04%"
            ), width=4)
        ])
    finally:
        print(f'[PERF] Callback: update_metrics - FIM - Tempo: {time.time() - start:.3f}s')

@app.callback(
    Output('atendimentos-graph', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_graph(year):
    start = time.time()
    print('[PERF] Callback: update_graph - INÍCIO')
    try:
        # Implementar o gráfico aqui
        return {}
    finally:
        print(f'[PERF] Callback: update_graph - FIM - Tempo: {time.time() - start:.3f}s')
''',
        'data/database.py': '''
import psycopg2
import pandas as pd

def get_db_connection():
    return psycopg2.connect(
        dbname='BI_GORE',
        user='postgres',
        password='postgre123',
        host='localhost'
    )

def fetch_atendimentos_data(year=None, month=None):
    start = time.time()
    print('[PERF] Query: fetch_atendimentos_data - INÍCIO')
    try:
        conn = get_db_connection()
        query = """
            SELECT *
            FROM dados_bi_gore
            WHERE 1=1
        """
        if year:
            query += f" AND EXTRACT(YEAR FROM data) = {year}"
        if month:
            query += f" AND EXTRACT(MONTH FROM data) = {month}"
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()
        print(f'[PERF] Query: fetch_atendimentos_data - FIM - Tempo: {time.time() - start:.3f}s')
''',
        'assets/css/style.css': '''
/* Estilos personalizados */
.card {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-title {
    color: #2c3e50;
    font-weight: bold;
}

.navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.container {
    padding-top: 20px;
    padding-bottom: 20px;
}
''',
        'index.py': '''
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from components.navbar import create_navbar
from layouts import atendimentos

app.layout = html.Div([
    create_navbar(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/atendimentos':
        return atendimentos.create_layout()
    return html.H1('Selecione uma opção no menu')

if __name__ == '__main__':
    app.run_server(debug=True)
'''
    }

    # Criar/atualizar os arquivos
    for file_path, content in files_content.items():
        full_path = os.path.join(base_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✅ Arquivo atualizado: {full_path}")

    print("\n✨ Arquivos do projeto atualizados com sucesso!")

if __name__ == "__main__":
    update_project_files()