import os
import time

def create_directory_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def write_file(filepath, content):
    directory = os.path.dirname(filepath)
    create_directory_if_not_exists(directory)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Conteúdo dos arquivos
layouts_atendimentos = '''
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
import pandas as pd
from data.database import execute_query

def get_available_years():
    query = """
        SELECT DISTINCT EXTRACT(YEAR FROM data_atendimento) as ano
        FROM dados_bi_gore
        ORDER BY ano DESC
    """
    years = execute_query(query)['ano'].tolist()
    return [{'label': 'TODOS', 'value': 'todos'}] + [{'label': str(int(year)), 'value': str(int(year))} for year in years]

def create_layout():
    return dbc.Container([
        html.H1("Dashboard de Atendimentos", className="dashboard-title"),
        dbc.Row([
            dbc.Col([
                html.Label("Ano"),
                html.Div([
                    dcc.Checklist(
                        id='year-checklist',
                        options=get_available_years(),
                        value=['todos'],
                        className="filter-checklist",
                        persistence=True
                    )
                ], style={'maxHeight': '200px', 'overflowY': 'auto'})
            ], width=2),
            dbc.Col([
                html.Label("Mês"),
                html.Div([
                    dcc.Checklist(
                        id='month-checklist',
                        options=[
                            {'label': 'TODOS', 'value': 'todos'},
                            {'label': 'Janeiro', 'value': '1'},
                            {'label': 'Fevereiro', 'value': '2'},
                            {'label': 'Março', 'value': '3'},
                            {'label': 'Abril', 'value': '4'},
                            {'label': 'Maio', 'value': '5'},
                            {'label': 'Junho', 'value': '6'},
                            {'label': 'Julho', 'value': '7'},
                            {'label': 'Agosto', 'value': '8'},
                            {'label': 'Setembro', 'value': '9'},
                            {'label': 'Outubro', 'value': '10'},
                            {'label': 'Novembro', 'value': '11'},
                            {'label': 'Dezembro', 'value': '12'}
                        ],
                        value=['todos'],
                        className="filter-checklist",
                        persistence=True
                    )
                ], style={'maxHeight': '200px', 'overflowY': 'auto'})
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
'''

callbacks_atendimentos = '''
from dash.dependencies import Input, Output, State
from app import app
import pandas as pd
import plotly.graph_objects as go
from data.database import execute_query
from datetime import datetime
from components.cards import create_metric_card
import dash_bootstrap_components as dbc

def get_atendimentos_data(years, months):
    start = time.time()
    print('[PERF] Query: get_atendimentos_data - INÍCIO')
    try:
        # Construir a query base
        where_clauses = []
        
        if 'todos' not in years:
            years_str = ','.join(years)
            where_clauses.append(f"EXTRACT(YEAR FROM data_atendimento) IN ({years_str})")
        
        if 'todos' not in months:
            months_str = ','.join(months)
            where_clauses.append(f"EXTRACT(MONTH FROM data_atendimento) IN ({months_str})")
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Query para dados atuais
        query_atual = f"""
            SELECT 
                COUNT(*) as total_atendimentos,
                COUNT(DISTINCT DATE(data_atendimento)) as dias_com_atendimento
            FROM dados_bi_gore
            WHERE {where_sql}
        """
        
        # Query para dados do período anterior
        years_anterior = [str(int(year) - 1) for year in years if year != 'todos']
        years_anterior_str = ','.join(years_anterior) if years_anterior else 'EXTRACT(YEAR FROM data_atendimento) - 1'
        
        where_anterior = f"EXTRACT(YEAR FROM data_atendimento) IN ({years_anterior_str})"
        if 'todos' not in months:
            where_anterior += f" AND EXTRACT(MONTH FROM data_atendimento) IN ({months_str})"
        
        query_anterior = f"""
            SELECT COUNT(*) as total_atendimentos
            FROM dados_bi_gore
            WHERE {where_anterior}
        """
        
        df_atual = execute_query(query_atual)
        df_anterior = execute_query(query_anterior)
        
        # Cálculos
        total_atual = df_atual['total_atendimentos'].iloc[0]
        total_anterior = df_anterior['total_atendimentos'].iloc[0]
        dias_atendimento = df_atual['dias_com_atendimento'].iloc[0]
        
        media_diaria = total_atual / dias_atendimento if dias_atendimento > 0 else 0
        media_diaria_anterior = total_anterior / dias_atendimento if dias_atendimento > 0 else 0
        
        dias_uteis_mes = 22
        projecao_mes = media_diaria * dias_uteis_mes
        
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
        print(f'[PERF] Query: get_atendimentos_data - FIM - Tempo: {time.time() - start:.3f}s')

def get_evolucao_data(years):
    start = time.time()
    print('[PERF] Query: get_evolucao_data - INÍCIO')
    try:
        if 'todos' in years:
            query = """
                WITH anos_disponiveis AS (
                    SELECT DISTINCT EXTRACT(YEAR FROM data_atendimento) as ano
                    FROM dados_bi_gore
                    ORDER BY ano DESC
                    LIMIT 2
                )
                SELECT 
                    EXTRACT(YEAR FROM data_atendimento) as ano,
                    EXTRACT(MONTH FROM data_atendimento) as mes,
                    COUNT(*) as total_atendimentos
                FROM dados_bi_gore
                WHERE EXTRACT(YEAR FROM data_atendimento) IN (SELECT ano FROM anos_disponiveis)
                GROUP BY EXTRACT(YEAR FROM data_atendimento), EXTRACT(MONTH FROM data_atendimento)
                ORDER BY ano, mes
            """
        else:
            years_str = ','.join(years)
            years_anterior = ','.join([str(int(year) - 1) for year in years])
            query = f"""
                SELECT 
                    EXTRACT(YEAR FROM data_atendimento) as ano,
                    EXTRACT(MONTH FROM data_atendimento) as mes,
                    COUNT(*) as total_atendimentos
                FROM dados_bi_gore
                WHERE EXTRACT(YEAR FROM data_atendimento) IN ({years_str}, {years_anterior})
                GROUP BY EXTRACT(YEAR FROM data_atendimento), EXTRACT(MONTH FROM data_atendimento)
                ORDER BY ano, mes
            """
        result = execute_query(query)
        return result
    finally:
        print(f'[PERF] Query: get_evolucao_data - FIM - Tempo: {time.time() - start:.3f}s')

# Callback para gerenciar a seleção "TODOS" nos anos
@app.callback(
    Output('year-checklist', 'value'),
    [Input('year-checklist', 'value')]
)
def manage_year_selection(selected_values):
    start = time.time()
    print('[PERF] Callback: manage_year_selection - INÍCIO')
    result = None
    try:
        if not selected_values:
            result = []
        elif 'todos' in selected_values:
            if len(selected_values) > 1:
                result = ['todos']
            else:
                result = selected_values
        else:
            result = selected_values
        return result
    finally:
        print(f'[PERF] Callback: manage_year_selection - FIM - Tempo: {time.time() - start:.3f}s')

# Callback similar para os meses
@app.callback(
    Output('month-checklist', 'value'),
    [Input('month-checklist', 'value')]
)
def manage_month_selection(selected_values):
    start = time.time()
    print('[PERF] Callback: manage_month_selection - INÍCIO')
    result = None
    try:
        if not selected_values:
            result = []
        elif 'todos' in selected_values:
            if len(selected_values) > 1:
                result = ['todos']
            else:
                result = selected_values
        else:
            result = selected_values
        return result
    finally:
        print(f'[PERF] Callback: manage_month_selection - FIM - Tempo: {time.time() - start:.3f}s')

@app.callback(
    Output('metrics-container', 'children'),
    [Input('year-checklist', 'value'),
     Input('month-checklist', 'value')]
)
def update_metrics(years, months):
    start = time.time()
    print('[PERF] Callback: update_metrics - INÍCIO')
    try:
        if not years or not months:
            return []
        data = get_atendimentos_data(years, months)
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
    [Input('year-checklist', 'value')]
)
def update_graph(years):
    start = time.time()
    print('[PERF] Callback: update_graph - INÍCIO')
    try:
        if not years:
            return {}
        df = get_evolucao_data(years)
        fig = go.Figure()
        anos = sorted(df['ano'].unique())
        for ano in anos:
            df_ano = df[df['ano'] == ano]
            fig.add_trace(go.Scatter(
                x=df_ano['mes'],
                y=df_ano['total_atendimentos'],
                name=f'Atendimentos {int(ano)}',
                line=dict(
                    color='#1a237e' if ano == max(anos) else '#90a4ae',
                    width=3 if ano == max(anos) else 2,
                    dash='solid' if ano == max(anos) else 'dash'
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
        return fig
    finally:
        print(f'[PERF] Callback: update_graph - FIM - Tempo: {time.time() - start:.3f}s')
'''

css_style = '''
.filter-checklist {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
}

.filter-checklist label {
    display: block;
    padding: 5px 0;
    cursor: pointer;
}

.filter-checklist input[type="checkbox"] {
    margin-right: 8px;
}
'''

# Atualizar os arquivos
files_to_update = {
    'layouts/atendimentos.py': layouts_atendimentos.strip(),
    'callbacks/atendimentos_callbacks.py': callbacks_atendimentos.strip(),
    'assets/css/style.css': css_style.strip()
}

def update_files():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for filepath, content in files_to_update.items():
        full_path = os.path.join(base_dir, filepath)
        write_file(full_path, content)
        print(f"Arquivo atualizado: {filepath}")

if __name__ == '__main__':
    update_files()
    print("Todos os arquivos foram atualizados com sucesso!")