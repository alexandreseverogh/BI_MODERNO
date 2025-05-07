import os
import time

def update_project_files():
    base_path = r"C:\falcao\GORE"
    
    files_content = {
        'index.py': '''
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from components.navbar import create_navbar
from layouts import atendimentos

def create_home_layout():
    return dbc.Container([
        html.Div([
            html.H1("GORE", className="home-title"),
            html.H2("Grupo de Oftalmologia de Recife", className="home-subtitle"),
            html.Hr(className="home-divider"),
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Atendimentos", className="menu-card-title"),
                            dbc.Button("Acessar", href="/atendimentos", color="primary", className="menu-button")
                        ])
                    ], className="menu-card")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Agendamentos", className="menu-card-title"),
                            dbc.Button("Acessar", href="/agendamentos", color="primary", className="menu-button")
                        ])
                    ], className="menu-card")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Convênios", className="menu-card-title"),
                            dbc.Button("Acessar", href="/convenios", color="primary", className="menu-button")
                        ])
                    ], className="menu-card")
                , width=4),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Contas a Pagar", className="menu-card-title"),
                            dbc.Button("Acessar", href="/contas-pagar", color="primary", className="menu-button")
                        ])
                    ], className="menu-card")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Contas a Receber", className="menu-card-title"),
                            dbc.Button("Acessar", href="/contas-receber", color="primary", className="menu-button")
                        ])
                    ], className="menu-card")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("DRE", className="menu-card-title"),
                            dbc.Button("Acessar", href="/dre", color="primary", className="menu-button")
                        ])
                    ], className="menu-card")
                , width=4),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Clientes", className="menu-card-title"),
                            dbc.Button("Acessar", href="/clientes", color="primary", className="menu-button")
                        ])
                    ], className="menu-card")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Dados Médicos", className="menu-card-title"),
                            dbc.Button("Acessar", href="/dados-medicos", color="primary", className="menu-button")
                        ])
                    ], className="menu-card")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Dados Brutos", className="menu-card-title"),
                            dbc.Button("Acessar", href="/dados-brutos", color="primary", className="menu-button")
                        ])
                    ], className="menu-card")
                , width=4),
            ])
        ], className="home-container")
    ])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    start = time.time()
    print('[PERF] Callback: display_page - INÍCIO')
    try:
        if pathname == '/':
            return create_home_layout()
        elif pathname == '/atendimentos':
            return html.Div([
                create_navbar(),
                atendimentos.create_layout()
            ])
        return create_home_layout()
    finally:
        print(f'[PERF] Callback: display_page - FIM - Tempo: {time.time() - start:.3f}s')

if __name__ == '__main__':
    app.run_server(debug=True)
''',
        'layouts/atendimentos.py': '''
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
import pandas as pd
from data.database import get_db_connection

def get_available_years():
    conn = get_db_connection()
    try:
        query = """
            SELECT DISTINCT EXTRACT(YEAR FROM data) as ano
            FROM dados_bi_gore
            ORDER BY ano DESC
        """
        years = pd.read_sql_query(query, conn)['ano'].tolist()
        return [{'label': 'TODOS', 'value': 'todos'}] + [{'label': str(int(year)), 'value': int(year)} for year in years]
    finally:
        conn.close()

def create_layout():
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    return dbc.Container([
        html.H1("Dashboard de Atendimentos", className="dashboard-title"),
        dbc.Row([
            dbc.Col([
                html.Label("Ano"),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=get_available_years(),
                    value='todos',
                    className="filter-dropdown"
                )
            ], width=2),
            dbc.Col([
                html.Label("Mês"),
                dcc.Dropdown(
                    id='month-dropdown',
                    options=[
                        {'label': 'TODOS', 'value': 'todos'},
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
                    value='todos',
                    className="filter-dropdown"
                )
            ], width=2)
        ], className="filter-container"),
        html.Div(id='metrics-container', className="metrics-container"),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Evolução de Atendimentos", className="chart-title"),
                        dcc.Graph(id='atendimentos-graph')
                    ])
                ),
                width=12
            )
        ], className="chart-container")
    ])
''',
        'callbacks/atendimentos_callbacks.py': '''
from dash.dependencies import Input, Output
from app import app
import pandas as pd
import plotly.graph_objects as go
from data.database import get_db_connection
from datetime import datetime
from components.cards import create_metric_card
import dash_bootstrap_components as dbc

def get_atendimentos_data(year, month):
    start = time.time()
    print('[PERF] Query: get_atendimentos_data - INÍCIO')
    try:
        conn = get_db_connection()
        # Construir a query base
        where_clauses = []
        if year != 'todos':
            where_clauses.append(f"EXTRACT(YEAR FROM data) = {year}")
        if month != 'todos':
            where_clauses.append(f"EXTRACT(MONTH FROM data) = {month}")
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Query para dados atuais
        query_atual = f"""
            SELECT 
                COUNT(*) as total_atendimentos,
                COUNT(DISTINCT DATE(data)) as dias_com_atendimento
            FROM dados_bi_gore
            WHERE {where_sql}
        """
        
        # Query para dados do período anterior
        year_anterior = int(year) - 1 if year != 'todos' else 'EXTRACT(YEAR FROM data) - 1'
        where_anterior = f"EXTRACT(YEAR FROM data) = {year_anterior}"
        if month != 'todos':
            where_anterior += f" AND EXTRACT(MONTH FROM data) = {month}"
        
        query_anterior = f"""
            SELECT COUNT(*) as total_atendimentos
            FROM dados_bi_gore
            WHERE {where_anterior}
        """
        
        df_atual = pd.read_sql_query(query_atual, conn)
        df_anterior = pd.read_sql_query(query_anterior, conn)
        
        # Cálculos
        total_atual = df_atual['total_atendimentos'].iloc[0]
        total_anterior = df_anterior['total_atendimentos'].iloc[0]
        dias_atendimento = df_atual['dias_com_atendimento'].iloc[0]
        
        media_diaria = total_atual / dias_atendimento if dias_atendimento > 0 else 0
        media_diaria_anterior = total_anterior / dias_atendimento if dias_atendimento > 0 else 0
        
        # Projeção para o mês inteiro
        dias_uteis_mes = 22  # média de dias úteis por mês
        projecao_mes = media_diaria * dias_uteis_mes
        
        # Cálculo das variações percentuais
        var_total = ((total_atual - total_anterior) / total_anterior * 100) if total_anterior > 0 else 0
        var_media = ((media_diaria - media_diaria_anterior) / media_diaria_anterior * 100) if media_diaria_anterior > 0 else 0
        var_projecao = ((projecao_mes - total_anterior) / total_anterior * 100) if total_anterior > 0 else 0
        
        result = {
            'total_atual': f"{total_atual:,.0f}",
            'total_anterior': f"{total_anterior:,.0f}",
            'var_total': f"{var_total:,.2f}%",
            'media_diaria': f"{media_diaria:,.0f}",
            'media_anterior': f"{media_diaria_anterior:,.0f}",
            'var_media': f"{var_media:,.2f}%",
            'projecao': f"{projecao_mes:,.0f}",
            'var_projecao': f"{var_projecao:,.2f}%"
        }
        return result
    finally:
        conn.close()
        print(f'[PERF] Query: get_atendimentos_data - FIM - Tempo: {time.time() - start:.3f}s')

def get_evolucao_data(year):
    start = time.time()
    print('[PERF] Query: get_evolucao_data - INÍCIO')
    try:
        conn = get_db_connection()
        # Se year for 'todos', pegamos os últimos 2 anos
        if year == 'todos':
            query = """
                WITH anos_disponiveis AS (
                    SELECT DISTINCT EXTRACT(YEAR FROM data) as ano
                    FROM dados_bi_gore
                    ORDER BY ano DESC
                    LIMIT 2
                )
                SELECT 
                    EXTRACT(YEAR FROM data) as ano,
                    EXTRACT(MONTH FROM data) as mes,
                    COUNT(*) as total_atendimentos
                FROM dados_bi_gore
                WHERE EXTRACT(YEAR FROM data) IN (SELECT ano FROM anos_disponiveis)
                GROUP BY EXTRACT(YEAR FROM data), EXTRACT(MONTH FROM data)
                ORDER BY ano, mes
            """
        else:
            query = f"""
                SELECT 
                    EXTRACT(YEAR FROM data) as ano,
                    EXTRACT(MONTH FROM data) as mes,
                    COUNT(*) as total_atendimentos
                FROM dados_bi_gore
                WHERE EXTRACT(YEAR FROM data) IN ({year}, {year-1})
                GROUP BY EXTRACT(YEAR FROM data), EXTRACT(MONTH FROM data)
                ORDER BY ano, mes
            """
        result = pd.read_sql_query(query, conn)
        return result
    finally:
        conn.close()
        print(f'[PERF] Query: get_evolucao_data - FIM - Tempo: {time.time() - start:.3f}s')

@app.callback(
    Output('metrics-container', 'children'),
    [Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_metrics(year, month):
    start = time.time()
    print('[PERF] Callback: update_metrics - INÍCIO')
    try:
        if not year or not month:
            return []
        data = get_atendimentos_data(year, month)
        return dbc.Row([
            dbc.Col(create_metric_card(
                "Qtde Acum Mês do Ano Atual",
                data['total_atual'],
                data['total_anterior'],
                data['var_total']
            ), width=4),
            dbc.Col(create_metric_card(
                "Qtde Méd Diária Mês do Ano Atual",
                data['media_diaria'],
                data['media_anterior'],
                data['var_media']
            ), width=4),
            dbc.Col(create_metric_card(
                "Proj Qtde p/ Mês do Ano Atual",
                data['projecao'],
                data['total_anterior'],
                data['var_projecao']
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
        if not year:
            return {}
        df = get_evolucao_data(year)
        fig = go.Figure()
        anos = df['ano'].unique()
        anos.sort()
        for ano in anos:
            df_ano = df[df['ano'] == ano]
            fig.add_trace(go.Scatter(
                x=df_ano['mes'],
                y=df_ano['total_atendimentos'],
                name=f'Atendimentos {int(ano)}',
                line=dict(
                    color='#1a237e' if ano == anos[-1] else '#90a4ae',
                    width=3 if ano == anos[-1] else 2,
                    dash='solid' if ano == anos[-1] else 'dash'
                )
            ))
        fig.update_layout(
            title='Evolução de Atendimentos',
            xaxis_title='Mês',
            yaxis_title='Quantidade de Atendimentos',
            template='plotly_white',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(
                family='Segoe UI',
                color='#2c3e50'
            )
        )
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f0f0f0',
            ticktext=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            tickvals=list(range(1, 13))
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f0f0f0'
        )
        return fig
    finally:
        print(f'[PERF] Callback: update_graph - FIM - Tempo: {time.time() - start:.3f}s')
''',
        'assets/css/style.css': '''
/* Estilos gerais */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f5f6fa;
}

/* Página inicial */
.home-container {
    text-align: center;
    padding: 3rem 0;
    max-width: 1200px;
    margin: 0 auto;
}

.home-title {
    font-size: 4rem;
    font-weight: bold;
    color: #1a237e;
    margin-bottom: 0.5rem;
    letter-spacing: 2px;
}

.home-subtitle {
    font-size: 1.8rem;
    color: #455a64;
    margin-bottom: 2rem;
}

.home-divider {
    width: 50%;
    margin: 2rem auto;
    border-top: 3px solid #1a237e;
}

.menu-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: none;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    height: 100%;
}

.menu-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.menu-card-title {
    color: #1a237e;
    font-weight: 600;
    margin-bottom: 1rem;
}

.menu-button {
    width: 100%;
    background-color: #1a237e !important;
    border-color: #1a237e !important;
}

.menu-button:hover {
    background-color: #0d47a1 !important;
    border-color: #0d47a1 !important;
}

/* Navbar personalizado */
.custom-navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 0.5rem 1rem;
    background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%) !important;
}

/* Dashboard */
.dashboard-title {
    color: #1a237e;
    margin-bottom: 2rem;
    font-weight: 600;
    font-size: 2rem;
}

.filter-container {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-dropdown {
    width: 100%;
}

.metrics-container {
    margin: 2rem 0;
}

.chart-container {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.chart-title {
    color: #1a237e;
    margin-bottom: 1.5rem;
    font-weight: 600;
}

/* Cards de métricas */
.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border-radius: 8px;
    padding: 1.5rem;
    height: 100%;
    transition: transform 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #1a237e;
    margin: 1rem 0;
}

.metric-comparison {
    font-size: 0.9rem;
    color: #757575;
}

.variation-positive {
    color: #4caf50;
    font-weight: 500;
}

.variation-negative {
    color: #f44336;
    font-weight: 500;
}
'''
    }
    
    for file_path, content in files_content.items():
        full_path = os.path.join(base_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✅ Arquivo atualizado: {full_path}")

    print("\n✨ Arquivos do projeto atualizados com sucesso!")

if __name__ == "__main__":
    update_project_files()