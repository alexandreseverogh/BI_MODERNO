import re
import hashlib
from dash import Input, Output, State, callback, html, ALL, MATCH, ctx, no_update, clientside_callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
from database.queries import (
    get_especialidades,
    get_formas_pagamento,
    get_profissionais,
    get_segmentos,
    get_total_atendimentos,
    get_valor_total,
    get_ticket_medio,
    get_atendimentos_por_mes,
    get_top_profissionais,
    get_years
)
import datetime

# Add debug counter
DEBUG_COUNTER = {'populate': 0, 'sync': 0, 'dashboard': 0}

def sanitize_id(id_str):
    # First convert to string and strip whitespace
    id_str = str(id_str).strip()
    
    # Replace any character that's not alphanumeric with a hyphen
    # This includes periods, slashes, spaces, and other special characters
    sanitized = re.sub(r'[^a-zA-Z0-9]+', '-', id_str)
    
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    
    # Ensure the ID is not empty and starts with a letter (Dash requirement)
    if not sanitized:
        sanitized = 'id'
    elif sanitized[0].isdigit():
        sanitized = 'n' + sanitized
        
    # Adiciona um hash do nome original para garantir unicidade absoluta
    hash_part = hashlib.md5(id_str.encode('utf-8')).hexdigest()[:8]
    return f"{sanitized}-{hash_part}"

# Cache available data at module level and handle blank values
def format_and_sort_items(items):
    formatted_items = []
    for item in items:
        nome = item['nome'].strip() if item['nome'] else "Em Branco"
        formatted_items.append({
            'id': item['id'],
            'nome': nome
        })
    # Sort by name, putting "Em Branco" at the beginning if it exists
    return sorted(formatted_items, key=lambda x: ("" if x['nome'] == "Em Branco" else x['nome']))

# Cache available data at module level with proper formatting
AVAILABLE_YEARS = get_years()
AVAILABLE_ESPECIALIDADES = format_and_sort_items(get_especialidades())
AVAILABLE_PAGAMENTOS = format_and_sort_items(get_formas_pagamento())
AVAILABLE_PROFISSIONAIS = format_and_sort_items(get_profissionais())
# Para segmentos, garantir ordem estável por nome
AVAILABLE_SEGMENTOS = sorted(format_and_sort_items(get_segmentos()), key=lambda x: x['nome'])

# Definir listas globais ordenadas e estáveis
ALL_ESPECIALIDADES = sorted(get_especialidades(), key=lambda x: x['nome'] if x['nome'] is not None else '')
ALL_PAGAMENTOS = sorted(get_formas_pagamento(), key=lambda x: x['nome'] if x['nome'] is not None else '')
ALL_PROFISSIONAIS = sorted(get_profissionais(), key=lambda x: x['nome'] if x['nome'] is not None else '')
ALL_SEGMENTOS = sorted(get_segmentos(), key=lambda x: x['nome'] if x['nome'] is not None else '')

@callback(
    [
        Output("especialidades-container", "children"),
        Output("pagamentos-container", "children"),
        Output("profissionais-container", "children"),
        Output("segmentos-container", "children")
    ],
    [
        Input({"type": "year-checkbox", "index": ALL}, "value"),
        Input({"type": "month-checkbox", "index": ALL}, "value"),
        Input("todos-anos-checkbox", "value"),
        Input("todos-meses-checkbox", "value")
    ],
    [
        State({"type": "especialidade-checkbox", "index": ALL}, "value"),
        State({"type": "pagamento-checkbox", "index": ALL}, "value"),
        State({"type": "profissional-checkbox", "index": ALL}, "value"),
        State({"type": "segmento-checkbox", "index": ALL}, "value"),
        State("todos-especialidades-checkbox", "value"),
        State("todos-pagamentos-checkbox", "value"),
        State("todos-profissionais-checkbox", "value"),
        State("todos-segmentos-checkbox", "value")
    ],
    prevent_initial_call=False
)
def populate_filter_options(
    year_values, month_values, 
    todos_anos_checked, todos_meses_checked,
    esp_states, pag_states, prof_states, segm_states,
    todos_esp_state, todos_pag_state, todos_prof_state, todos_segm_state
):
    # Get the selected years and months
    selected_years = []
    if todos_anos_checked:
        selected_years = [str(year) for year in AVAILABLE_YEARS]
    else:
        if year_values:  # If we have values, use them
            selected_years = [str(year) for year, checked in zip(AVAILABLE_YEARS, year_values) if checked]
        else:  # If no values (initial state), select all years
            selected_years = [str(year) for year in AVAILABLE_YEARS]

    selected_months = []
    if todos_meses_checked:
        selected_months = [str(month) for month in range(1, 13)]
    else:
        if month_values:  # If we have values, use them
            selected_months = [str(month) for month, checked in zip(range(1, 13), month_values) if checked]
        else:  # If no values (initial state), select all months
            selected_months = [str(month) for month in range(1, 13)]

    # Initialize states if they don't exist
    if not esp_states:
        esp_states = [True] * len(AVAILABLE_ESPECIALIDADES)
    if not pag_states:
        pag_states = [True] * len(AVAILABLE_PAGAMENTOS)
    if not prof_states:
        prof_states = [True] * len(AVAILABLE_PROFISSIONAIS)
    if not segm_states:
        segm_states = [True] * len(AVAILABLE_SEGMENTOS)

    # Create the checkbox components with preserved states
    especialidades_checkboxes = [
        dbc.Checkbox(
            id={"type": "especialidade-checkbox", "index": item['nome']},
            label=item['nome'],
            value=state,
            className="d-block"
        ) for item, state in zip(AVAILABLE_ESPECIALIDADES, esp_states)
    ]

    pagamentos_checkboxes = [
        dbc.Checkbox(
            id={"type": "pagamento-checkbox", "index": item['nome']},
            label=item['nome'],
            value=state,
            className="d-block"
        ) for item, state in zip(AVAILABLE_PAGAMENTOS, pag_states)
    ]

    profissionais_checkboxes = [
        dbc.Checkbox(
            id={"type": "profissional-checkbox", "index": item['nome']},
            label=item['nome'],
            value=state,
            className="d-block"
        ) for item, state in zip(AVAILABLE_PROFISSIONAIS, prof_states)
    ]

    segmentos_checkboxes = [
        dbc.Checkbox(
            id={"type": "segmento-checkbox", "index": item['nome']},
            label=item['nome'],
            value=state,
            className="d-block"
        ) for item, state in zip(AVAILABLE_SEGMENTOS, segm_states)
    ]

    return [
        html.Div(especialidades_checkboxes, id="especialidades-checkboxes-container"),
        html.Div(pagamentos_checkboxes, id="pagamentos-checkboxes-container"),
        html.Div(profissionais_checkboxes, id="profissionais-checkboxes-container"),
        html.Div(segmentos_checkboxes, id="segmentos-checkboxes-container")
    ]

# Improved year checkbox synchronization
@callback(
    [Output({"type": "year-checkbox", "index": ALL}, "value"),
     Output("todos-anos-checkbox", "value")],
    [Input("todos-anos-checkbox", "value"),
     Input({"type": "year-checkbox", "index": ALL}, "value")],
    prevent_initial_call=False
)
def sync_year_checkboxes(todos_value, year_values):
    if not ctx.triggered:
        # Initial state - everything selected
        years = get_years()
        return [[True] * len(years), True]
    
    trigger_id = ctx.triggered_id
    years = get_years()
    n_years = len(years)
    
    if trigger_id == "todos-anos-checkbox":
        # If todos_value is None or False, uncheck all
        if not todos_value:
            return [[False] * n_years, False]
        # If todos_value is True, check all
        return [[True] * n_years, True]
    else:
        # If no year values provided, treat as all unchecked
        if not year_values:
            return [[False] * n_years, False]
        
        # Check if all are selected or none are selected
        all_checked = all(year_values)
        none_checked = not any(year_values)
        
        if none_checked:
            return [[False] * n_years, False]
        elif all_checked:
            return [[True] * n_years, True]
        else:
            # Some are checked, some aren't
            return [year_values, False]

# Improved month checkbox synchronization
@callback(
    [Output({"type": "month-checkbox", "index": ALL}, "value"),
     Output("todos-meses-checkbox", "value")],
    [Input("todos-meses-checkbox", "value"),
     Input({"type": "month-checkbox", "index": ALL}, "value")],
    prevent_initial_call=False
)
def sync_month_checkboxes(todos_value, month_values):
    if not ctx.triggered:
        # Initial state - everything selected
        return [[True] * 12, True]
    
    trigger_id = ctx.triggered_id
    n_months = 12
    
    if trigger_id == "todos-meses-checkbox":
        # If todos_value is None or False, uncheck all
        if not todos_value:
            return [[False] * n_months, False]
        # If todos_value is True, check all
        return [[True] * n_months, True]
    else:
        # If no month values provided, treat as all unchecked
        if not month_values:
            return [[False] * n_months, False]
        
        # Check if all are selected or none are selected
        all_checked = all(month_values)
        none_checked = not any(month_values)
        
        if none_checked:
            return [[False] * n_months, False]
        elif all_checked:
            return [[True] * n_months, True]
        else:
            # Some are checked, some aren't
            return [month_values, False]

# Improved specialty checkbox synchronization
@callback(
    [Output({"type": "especialidade-checkbox", "index": ALL}, "value"),
     Output("todos-especialidades-checkbox", "value")],
    [Input("todos-especialidades-checkbox", "value"),
     Input({"type": "especialidade-checkbox", "index": ALL}, "value")],
    prevent_initial_call=True
)
def sync_especialidade_checkboxes(todos_value, esp_values):
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered_id
    n_especialidades = len(AVAILABLE_ESPECIALIDADES)
    
    # If triggered by individual checkbox
    if isinstance(trigger_id, dict):
        if not esp_values:
            return [[False] * n_especialidades, False]
        
        # TODOS só deve estar marcado se realmente todas as opções estiverem marcadas
        all_checked = all(esp_values)
        return [esp_values, all_checked]
    
    # If triggered by TODOS checkbox
    if todos_value is None:
        raise PreventUpdate
        
    return [[todos_value] * n_especialidades, todos_value]

# Improved payment method checkbox synchronization
@callback(
    [Output({"type": "pagamento-checkbox", "index": ALL}, "value"),
     Output("todos-pagamentos-checkbox", "value")],
    [Input("todos-pagamentos-checkbox", "value"),
     Input({"type": "pagamento-checkbox", "index": ALL}, "value")],
    prevent_initial_call=True
)
def sync_pagamento_checkboxes(todos_value, pag_values):
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered_id
    n_pagamentos = len(AVAILABLE_PAGAMENTOS)
    
    # If triggered by individual checkbox
    if isinstance(trigger_id, dict):
        if not pag_values:
            return [[False] * n_pagamentos, False]
        
        # TODOS só deve estar marcado se realmente todas as opções estiverem marcadas
        all_checked = all(pag_values)
        return [pag_values, all_checked]
    
    # If triggered by TODOS checkbox
    if todos_value is None:
        raise PreventUpdate
        
    return [[todos_value] * n_pagamentos, todos_value]

# Improved professional checkbox synchronization
@callback(
    [Output({"type": "profissional-checkbox", "index": ALL}, "value"),
     Output("todos-profissionais-checkbox", "value")],
    [Input("todos-profissionais-checkbox", "value"),
     Input({"type": "profissional-checkbox", "index": ALL}, "value")],
    prevent_initial_call=True
)
def sync_profissional_checkboxes(todos_value, prof_values):
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered_id
    n_profissionais = len(AVAILABLE_PROFISSIONAIS)
    
    # If triggered by individual checkbox
    if isinstance(trigger_id, dict):
        if not prof_values:
            return [[False] * n_profissionais, False]
        
        # TODOS só deve estar marcado se realmente todas as opções estiverem marcadas
        all_checked = all(prof_values)
        return [prof_values, all_checked]
    
    # If triggered by TODOS checkbox
    if todos_value is None:
        raise PreventUpdate
        
    return [[todos_value] * n_profissionais, todos_value]

# Improved segmento checkbox synchronization
@callback(
    [Output({"type": "segmento-checkbox", "index": ALL}, "value"),
     Output("todos-segmentos-checkbox", "value")],
    [Input("todos-segmentos-checkbox", "value"),
     Input({"type": "segmento-checkbox", "index": ALL}, "value")],
    prevent_initial_call=True
)
def sync_segmento_checkboxes(todos_value, segm_values):
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered_id
    # Garantir ordem estável dos segmentos
    n_segmentos = len(AVAILABLE_SEGMENTOS)
    
    # If triggered by individual checkbox
    if isinstance(trigger_id, dict):
        if not segm_values:
            return [[False] * n_segmentos, False]
        # TODOS só deve estar marcado se realmente todas as opções estiverem marcadas
        all_checked = all(segm_values)
        return [segm_values, all_checked]
    
    # If triggered by TODOS checkbox
    if todos_value is None:
        raise PreventUpdate
        
    return [[todos_value] * n_segmentos, todos_value]

def get_color_for_year(index):
    base_colors = [
        '#1f77b4',  # azul
        '#2ca02c',  # verde
        '#ff7f0e',  # laranja
        '#d62728',  # vermelho
        '#9467bd',  # roxo
        '#8c564b',  # marrom
        '#e377c2',  # rosa
        '#7f7f7f',  # cinza
        '#bcbd22',  # oliva
        '#17becf'   # ciano
    ]
    return base_colors[index % len(base_colors)]

def organize_monthly_data(atendimentos_mes, years):
    # Criar um dicionário para armazenar os dados por ano
    data_by_year = {year: [0] * 12 for year in years}
    
    # Preencher os dados existentes
    for row in atendimentos_mes:
        year = int(row['ano'])
        month = int(row['mes']) - 1  # Ajustar para índice 0-11
        if year in data_by_year:
            data_by_year[year][month] = row['atendimentos']
    
    return data_by_year

def converter_para_iso(data_str):
    if not data_str:
        return None
    try:
        return datetime.datetime.strptime(data_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except Exception:
        try:
            return datetime.datetime.strptime(data_str, '%Y-%m-%d').strftime('%Y-%m-%d')
        except Exception:
            return None

@callback(
    [
        Output("total-atendimentos", "children"),
        Output("valor-total", "children"),
        Output("ticket-medio", "children"),
        Output("atendimentos-mensais", "figure"),
        Output("top-profissionais", "figure")
    ],
    [
        Input({"type": "year-checkbox", "index": ALL}, "value"),
        Input({"type": "month-checkbox", "index": ALL}, "value"),
        Input({"type": "especialidade-checkbox", "index": ALL}, "value"),
        Input({"type": "pagamento-checkbox", "index": ALL}, "value"),
        Input({"type": "profissional-checkbox", "index": ALL}, "value"),
        Input({"type": "segmento-checkbox", "index": ALL}, "value"),
        Input("todos-anos-checkbox", "value"),
        Input("todos-meses-checkbox", "value"),
        Input("todos-especialidades-checkbox", "value"),
        Input("todos-pagamentos-checkbox", "value"),
        Input("todos-profissionais-checkbox", "value"),
        Input("todos-segmentos-checkbox", "value"),
        Input("data_inicial", "date"),
        Input("data_final", "date")
    ],
    prevent_initial_call=False
)
def update_dashboard(
    year_values, month_values,
    especialidade_values, pagamento_values,
    profissional_values, segmento_values,
    todos_anos, todos_meses,
    todos_especialidades, todos_pagamentos,
    todos_profissionais, todos_segmentos,
    data_inicial, data_final
):
    try:
        # Get years
        years = get_years()
        if todos_anos:
            selected_years = [str(year) for year in years]
        else:
            if year_values is None:
                selected_years = []
            else:
                selected_years = [str(year) for year, checked in zip(years, year_values) if checked]

        if todos_meses:
            selected_months = [str(month) for month in range(1, 13)]
        else:
            if month_values is None:
                selected_months = []
            else:
                selected_months = [str(month) for month, checked in zip(range(1, 13), month_values) if checked]

        # Coletar os IDs dos checkboxes selecionados usando ctx.inputs_list
        # Especialidades
        esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
        selected_especialidades = [esp_id for esp_id, checked in zip(esp_ids, especialidade_values) if checked]
        # Pagamentos
        pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
        selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
        # Profissionais
        prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
        selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
        # Segmentos
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]

        # Ajuste: se todas as opções de um filtro estão selecionadas, não aplicar filtro (enviar lista vazia)
        if set(selected_years) == set([str(year) for year in years]):
            selected_years = []
        if set(selected_months) == set([str(month) for month in range(1, 13)]):
            selected_months = []
        if set(selected_especialidades) == set(esp_ids):
            selected_especialidades = []
        if set(selected_pagamentos) == set(pag_ids):
            selected_pagamentos = []
        if set(selected_profissionais) == set(prof_ids):
            selected_profissionais = []
        if set(selected_segmentos) == set(segm_ids):
            selected_segmentos = []

        # DEBUG PRINTS DOS FILTROS
        print("\nDEBUG - Filtros aplicados:")
        print("Anos:", selected_years)
        print("Meses:", selected_months)
        print("Especialidades:", selected_especialidades)
        print("Pagamentos:", selected_pagamentos)
        print("Profissionais:", selected_profissionais)
        print("Segmentos:", selected_segmentos)

        # Se o usuário desmarcou todas as opções de algum filtro, mostrar dashboard vazio
        if (
            (not selected_years and not todos_anos) or
            (not selected_months and not todos_meses) or
            (not selected_especialidades and not todos_especialidades) or
            (not selected_pagamentos and not todos_pagamentos) or
            (not selected_profissionais and not todos_profissionais) or
            (not selected_segmentos and not todos_segmentos)
        ):
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Sem dados para exibir",
                annotations=[{
                    'text': "Selecione pelo menos uma opção em cada filtro",
                    'xref': "paper",
                    'yref': "paper",
                    'showarrow': False,
                    'font': {'size': 20}
                }]
            )
            return [
                "0",
                "R$ 0,00",
                "R$ 0,00",
                empty_fig,
                empty_fig
            ]

        # Conversão das datas para o formato do banco
        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)

        # Get the dataselected_years
        total_atendimentos = get_total_atendimentos(
            selected_years, selected_months,
            selected_especialidades, selected_pagamentos,
            selected_profissionais, selected_segmentos,
            data_inicial=data_inicial_iso, data_final=data_final_iso
        )

        total_valor = get_valor_total(
            selected_years, selected_months,
            selected_especialidades, selected_pagamentos,
            selected_profissionais, selected_segmentos,
            data_inicial=data_inicial_iso, data_final=data_final_iso
        )

        ticket_medio = total_valor / total_atendimentos if total_atendimentos > 0 else 0

        # Get data for charts
        atendimentos_mes = get_atendimentos_por_mes(
            selected_years, selected_months,
            selected_especialidades, selected_pagamentos,
            selected_profissionais, selected_segmentos,
            data_inicial=data_inicial_iso, data_final=data_final_iso
        )

        top_profissionais = get_top_profissionais(
            selected_years, selected_months,
            selected_especialidades, selected_pagamentos,
            selected_profissionais, selected_segmentos,
            data_inicial=data_inicial_iso, data_final=data_final_iso
        )

        # Organizar dados por mês (garantir 12 meses no eixo X)
        meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        atendimentos_por_mes = [0] * 12  # Inicializa com zero
        for row in atendimentos_mes:
            mes_idx = int(row['mes']) - 1  # meses de 1 a 12
            atendimentos_por_mes[mes_idx] = row['atendimentos']

        fig_atendimentos = go.Figure()
        fig_atendimentos.add_trace(go.Scatter(
            x=meses_labels,
            y=atendimentos_por_mes,
            mode='lines+markers',
            name='Total de Atendimentos',
            line=dict(color='#2196f3')
        ))
        fig_atendimentos.update_layout(
            title="Atendimentos por Mês",
            xaxis_title="Mês",
            yaxis_title="Total de Atendimentos",
            showlegend=False,
            template="plotly_dark",
            paper_bgcolor="#23272f",
            plot_bgcolor="#23272f",
            font_color="#fff",
            xaxis=dict(color="#fff", gridcolor="#444"),
            yaxis=dict(color="#fff", gridcolor="#444"),
            legend=dict(font=dict(color="#fff")),
            margin=dict(l=20, r=20, t=40, b=20)
        )

        # Gráfico de top profissionais permanece como barras
        fig_profissionais = go.Figure(data=[
            go.Bar(
                x=[row['nome'] for row in top_profissionais],
                y=[row['atendimentos'] for row in top_profissionais],
                marker_color='rgb(55, 83, 109)'
            )
        ])
        fig_profissionais.update_layout(
            title="Top Profissionais",
            xaxis_title="Profissional",
            yaxis_title="Total de Atendimentos",
            showlegend=False,
            template="plotly_dark",
            paper_bgcolor="#23272f",
            plot_bgcolor="#23272f",
            font_color="#fff",
            xaxis=dict(color="#fff", gridcolor="#444"),
            yaxis=dict(color="#fff", gridcolor="#444"),
            legend=dict(font=dict(color="#fff")),
            margin=dict(l=20, r=20, t=40, b=20)
        )

        # Se existirem gráficos extras, aplicar o tema dark neles também
        if 'fig_extra_1' in locals():
            fig_extra_1.update_layout(
                template="plotly_dark",
                paper_bgcolor="#23272f",
                plot_bgcolor="#23272f",
                font_color="#fff",
                xaxis=dict(color="#fff", gridcolor="#444"),
                yaxis=dict(color="#fff", gridcolor="#444"),
                legend=dict(font=dict(color="#fff")),
                margin=dict(l=20, r=20, t=40, b=20)
            )
        if 'fig_extra_2' in locals():
            fig_extra_2.update_layout(
                template="plotly_dark",
                paper_bgcolor="#23272f",
                plot_bgcolor="#23272f",
                font_color="#fff",
                xaxis=dict(color="#fff", gridcolor="#444"),
                yaxis=dict(color="#fff", gridcolor="#444"),
                legend=dict(font=dict(color="#fff")),
                margin=dict(l=20, r=20, t=40, b=20)
            )

        return [
            f"{total_atendimentos:,}".replace(",", "."),
            f"R$ {total_valor:,.2f}".replace(",", "."),
            f"R$ {ticket_medio:,.2f}".replace(",", "."),
            fig_atendimentos,
            fig_profissionais
        ]
    except Exception as e:
        import traceback
        print("ERRO NO CALLBACK update_dashboard:")
        traceback.print_exc()
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Erro no callback",
            annotations=[{
                'text': str(e),
                'xref': "paper",
                'yref': "paper",
                'showarrow': False,
                'font': {'size': 20}
            }]
        )
        return ["0", "R$ 0,00", "R$ 0,00", empty_fig, empty_fig]

# Collapse para CONVENIOS
@callback(
    Output("collapse-pagamentos", "is_open"),
    Input("collapse-pagamentos-btn", "n_clicks"),
    State("collapse-pagamentos", "is_open"),
)
def toggle_collapse_pagamentos(n, is_open):
    if n:
        return not is_open
    return is_open

# Collapse para MEDICOS
@callback(
    Output("collapse-profissionais", "is_open"),
    Input("collapse-profissionais-btn", "n_clicks"),
    State("collapse-profissionais", "is_open"),
)
def toggle_collapse_profissionais(n, is_open):
    if n:
        return not is_open
    return is_open

# Collapse para PROCEDIMENTOS
@callback(
    Output("collapse-especialidades", "is_open"),
    Input("collapse-especialidades-btn", "n_clicks"),
    State("collapse-especialidades", "is_open"),
)
def toggle_collapse_especialidades(n, is_open):
    if n:
        return not is_open
    return is_open

# Collapse para SEGMENTOS
@callback(
    Output("collapse-segmentos", "is_open"),
    Input("collapse-segmentos-btn", "n_clicks"),
    State("collapse-segmentos", "is_open"),
)
def toggle_collapse_segmentos(n, is_open):
    if n:
        return not is_open
    return is_open