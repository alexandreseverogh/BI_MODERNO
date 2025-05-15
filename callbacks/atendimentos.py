import re
import hashlib
import dash
from dash import Input, Output, State, callback, html, ALL, MATCH, ctx, no_update, clientside_callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import callback_context
import plotly.express as px
import pandas as pd
import time
from dash_bootstrap_templates import ThemeSwitchAIO, load_figure_template
from database.queries import (
    get_formas_pagamento,
    get_profissionais,
    get_segmentos,
    get_tipos_atendimento,
    get_total_atendimentos,
    get_valor_total,
    get_ticket_medio,
    get_atendimentos_por_mes,
    get_top_profissionais,
    get_years,
    get_atendimentos_por_tipo_atendimento_ano,
    build_filter_conditions,
    engine,
    get_atendimentos_por_ano,
    get_total_procedimentos,
    get_valor_total_por_medico_ano,
    get_total_procedimentos_por_ano,
    get_procedimentos_por_medico_ano,
    get_dados_filtrados,
    get_dados_agrupados
)
import datetime
from pages.atendimentos import get_graph_theme_settings
import plotly.graph_objects as go
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from dash import dash_table
from functools import wraps
import io
from dash import dcc
from dash import callback_context

# Load the figure templates for both themes
load_figure_template(["flatly", "darkly"])

# Add debug counter
DEBUG_COUNTER = {'populate': 0, 'sync': 0, 'dashboard': 0}

SEGMENTOS_PER_PAGE = 20

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
AVAILABLE_PAGAMENTOS = format_and_sort_items(get_formas_pagamento())
AVAILABLE_PROFISSIONAIS = format_and_sort_items(get_profissionais())
# Para segmentos, garantir ordem estável por nome e padronizar 'Em Branco'
AVAILABLE_SEGMENTOS = sorted(format_and_sort_items(get_segmentos()), key=lambda x: x['nome'])
AVAILABLE_TIPOS_ATENDIMENTO = format_and_sort_items(get_tipos_atendimento())

# Definir listas globais ordenadas e estáveis
ALL_PAGAMENTOS = sorted(get_formas_pagamento(), key=lambda x: x['nome'] if x['nome'] is not None else '')
ALL_PROFISSIONAIS = sorted(get_profissionais(), key=lambda x: x['nome'] if x['nome'] is not None else '')
ALL_SEGMENTOS = sorted(format_and_sort_items(get_segmentos()), key=lambda x: x['nome'])
ALL_TIPOS_ATENDIMENTO = sorted(format_and_sort_items(get_tipos_atendimento()), key=lambda x: x['nome'])

def log_tempo_callback(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"[TIMER] Início callback {func.__name__}")
        try:
            return func(*args, **kwargs)
        finally:
            print(f"[TIMER] Fim callback {func.__name__}: {time.time() - start:.3f}s")
    return wrapper

def log_tempo_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"[TIMER] Início query {func.__name__}")
        try:
            return func(*args, **kwargs)
        finally:
            print(f"[TIMER] Fim query {func.__name__}: {time.time() - start:.3f}s")
    return wrapper

@callback(
    [
        Output("pagamentos-container", "children"),
        Output("profissionais-container", "children")
    ],
    [
        Input({"type": "year-checkbox", "index": ALL}, "value"),
        Input({"type": "month-checkbox", "index": ALL}, "value"),
        Input("todos-anos-checkbox", "value"),
        Input("todos-meses-checkbox", "value")
    ],
    [
        State({"type": "pagamento-checkbox", "index": ALL}, "value"),
        State({"type": "profissional-checkbox", "index": ALL}, "value"),
        State({"type": "segmento-checkbox", "index": ALL}, "value"),
        State("todos-pagamentos-checkbox", "value"),
        State("todos-profissionais-checkbox", "value")
    ],
    prevent_initial_call=False
)
def populate_filter_options(
    year_values, month_values, 
    todos_anos_checked, todos_meses_checked,
    pagamento_states, profissional_states, segmento_states,
    todos_pagamentos_state, todos_profissionais_state
):
    try:
        pagamentos = AVAILABLE_PAGAMENTOS
        profissionais = AVAILABLE_PROFISSIONAIS
        # Inicializar estados corretamente
        if not pagamento_states or len(pagamento_states) != len(pagamentos):
            pagamento_states = [True] * len(pagamentos)
        if not profissional_states or len(profissional_states) != len(profissionais):
            profissional_states = [True] * len(profissionais)
        pagamentos_checkboxes = [
            dbc.Checkbox(
                id={"type": "pagamento-checkbox", "index": item['nome']},
                label=item['nome'],
                value=state if state is not None else True,
                className="d-block"
            ) for item, state in zip(pagamentos, pagamento_states)
        ]
        profissionais_checkboxes = [
            dbc.Checkbox(
                id={"type": "profissional-checkbox", "index": item['nome']},
                label=item['nome'],
                value=state if state is not None else True,
                className="d-block"
            ) for item, state in zip(profissionais, profissional_states)
        ]
        return [
            html.Div(pagamentos_checkboxes, id="pagamentos-checkboxes-container"),
            html.Div(profissionais_checkboxes, id="profissionais-checkboxes-container")
        ]
    except Exception as e:
        print("[ERRO] populate_filter_options:", e)
        import traceback; traceback.print_exc()
        return [[], []]

# Improved year checkbox synchronization
@callback(
    [Output({"type": "year-checkbox", "index": ALL}, "value"),
     Output("todos-anos-checkbox", "value")],
    [Input("todos-anos-checkbox", "value"),
     Input({"type": "year-checkbox", "index": ALL}, "value")],
    prevent_initial_call=False
)
@log_tempo_callback
def sync_year_checkboxes(todos_value, year_values):
    from dash import ctx
    years = get_years()
    n_years = len(years)
    trigger_id = ctx.triggered_id
    if trigger_id == "todos-anos-checkbox":
        if todos_value:
            # Desmarcar tudo
            return [[False] * n_years, False]
        else:
            # Marcar tudo
            return [[True] * n_years, True]
    else:
        if not year_values:
            return [[False] * n_years, False]
        all_checked = all(year_values)
        if all_checked:
            return [year_values, True]
        else:
            return [year_values, False]

# Improved month checkbox synchronization
@callback(
    [Output({"type": "month-checkbox", "index": ALL}, "value"),
     Output("todos-meses-checkbox", "value")],
    [Input("todos-meses-checkbox", "value"),
     Input({"type": "month-checkbox", "index": ALL}, "value")],
    prevent_initial_call=False
)
@log_tempo_callback
def sync_month_checkboxes(todos_value, month_values):
    from dash import ctx
    n_months = 12
    trigger_id = ctx.triggered_id
    if trigger_id == "todos-meses-checkbox":
        if todos_value:
            return [[False] * n_months, False]
        else:
            return [[True] * n_months, True]
    else:
        if not month_values:
            return [[False] * n_months, False]
        all_checked = all(month_values)
        if all_checked:
            return [month_values, True]
        else:
            return [month_values, False]

@callback(
    [Output({"type": "pagamento-checkbox", "index": ALL}, "value"),
     Output("todos-pagamentos-checkbox", "value")],
    [Input("todos-pagamentos-checkbox", "value"),
     Input({"type": "pagamento-checkbox", "index": ALL}, "value")],
    prevent_initial_call=False
)
def sync_pagamento_checkboxes(todos_value, pagamento_values):
    from dash import ctx
    trigger_id = ctx.triggered_id
    n = len(pagamento_values)
    def is_checked(val):
        if isinstance(val, list):
            return bool(val)
        return bool(val)
    todos_checked = is_checked(todos_value)
    if trigger_id == "todos-pagamentos-checkbox":
        if todos_checked:
            return [ [True]*n, True ]
        else:
            return [ [False]*n, False ]
    else:
        all_checked = all(pagamento_values)
        any_checked = any(pagamento_values)
        if all_checked:
            return [ pagamento_values, True ]
        elif not any_checked:
            return [ pagamento_values, False ]
        else:
            return [ pagamento_values, False ]

@callback(
    [Output({"type": "profissional-checkbox", "index": ALL}, "value"),
     Output("todos-profissionais-checkbox", "value")],
    [Input("todos-profissionais-checkbox", "value"),
     Input({"type": "profissional-checkbox", "index": ALL}, "value")],
    prevent_initial_call=False
)
@log_tempo_callback
def sync_profissional_checkboxes(todos_value, profissional_values):
    from dash import ctx
    import copy
    trigger_id = ctx.triggered_id
    n = len(profissional_values)
    # Dash pode passar True, False, ["TODOS"], [] ou None
    def is_checked(val):
        if isinstance(val, list):
            return bool(val)
        return bool(val)
    todos_checked = is_checked(todos_value)
    # Se o trigger foi o botão TODOS
    if trigger_id == "todos-profissionais-checkbox":
        if todos_checked:
            # Marcar todos
            return [ [True]*n, True ]
        else:
            # Desmarcar todos
            return [ [False]*n, False ]
    # Se o trigger foi algum individual
    else:
        all_checked = all(profissional_values)
        any_checked = any(profissional_values)
        # Se todos marcados, marcar TODOS
        if all_checked:
            return [ profissional_values, True ]
        # Se nenhum marcado, desmarcar TODOS
        elif not any_checked:
            return [ profissional_values, False ]
        # Se alguns marcados, desmarcar TODOS
        else:
            return [ profissional_values, False ]

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
    Output("collapse-procedimentos", "is_open"),
    Input("collapse-procedimentos-btn", "n_clicks"),
    State("collapse-procedimentos", "is_open"),
)
def toggle_collapse_procedimentos(n, is_open):
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

# Add callback to update colors based on theme
@callback(
    [
        Output("producao-medica-title", "style"),
        Output("convenios-title", "style"),
        Output("medicos-title", "style"),
        Output("procedimentos-title", "style"),
        Output("collapse-pagamentos-btn", "style"),
        Output("collapse-profissionais-btn", "style"),
        Output("collapse-segmentos-btn", "style"),
        Output("collapse-procedimentos-btn", "style"),  # Adicionado para PROCEDIMENTOS
        Output("todos-anos-checkbox", "className"),
        Output("todos-meses-checkbox", "className"),
        Output("todos-pagamentos-checkbox", "className"),
        Output("todos-profissionais-checkbox", "className"),
        Output("todos-segmentos-checkbox", "className")
    ],
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def update_theme_dependent_styles(theme_toggle):
    button_color = "#006400" if theme_toggle else "#90EE90"
    title_color = "#000000" if theme_toggle else "#FFFFFF"
    title_style = {"color": title_color}
    button_style = {"color": button_color}
    checkbox_class = "d-inline-block me-2 custom-checkbox " + ("theme-light" if theme_toggle else "theme-dark")
    return (
        [title_style] * 4 +  # Estilos dos títulos
        [button_style] * 4 + # Agora 4 botões
        [checkbox_class] * 5  # Classes dos checkboxes
    )

@callback(
    Output("atendimentos-por-procedimento-ano", "figure"),
    [
        Input({"type": "year-checkbox", "index": ALL}, "value"),
        Input({"type": "month-checkbox", "index": ALL}, "value"),
        Input({"type": "segmento-checkbox", "index": ALL}, "value"),
        Input({"type": "pagamento-checkbox", "index": ALL}, "value"),
        Input({"type": "profissional-checkbox", "index": ALL}, "value"),
        Input({"type": "segmento-checkbox", "index": ALL}, "value"),
        Input("todos-anos-checkbox", "value"),
        Input("todos-meses-checkbox", "value"),
        Input("todos-segmentos-checkbox", "value"),
        Input("todos-pagamentos-checkbox", "value"),
        Input("todos-profissionais-checkbox", "value"),
        Input("todos-segmentos-checkbox", "value"),
        Input("data_inicial", "date"),
        Input("data_final", "date"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value")
    ],
    prevent_initial_call='initial_duplicate'
)
@log_tempo_callback
def update_atendimentos_por_procedimento_ano(
    year_values, month_values,
    tipo_atendimento_values, pagamento_values,
    profissional_values, segmento_values,
    todos_anos, todos_meses,
    todos_tipos_atendimento, todos_pagamentos,
    todos_profissionais, todos_segmentos,
    data_inicial, data_final,
    theme_toggle
):
    try:
        from dash import ctx
        import pandas as pd
        import plotly.graph_objects as go
        from database.queries import get_dados_agrupados
        theme_settings = get_graph_theme_settings(theme_toggle)
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
        esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
        selected_tipos_atendimento = [esp_id for esp_id, checked in zip(esp_ids, tipo_atendimento_values) if checked]
        pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
        selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
        prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
        selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]
        if set(selected_years) == set([str(year) for year in years]):
            selected_years = []
        if set(selected_months) == set([str(month) for month in range(1, 13)]):
            selected_months = []
        if set(selected_tipos_atendimento) == set(esp_ids):
            selected_tipos_atendimento = []
        if set(selected_pagamentos) == set(pag_ids):
            selected_pagamentos = []
        if set(selected_profissionais) == set(prof_ids):
            selected_profissionais = []
        if set(selected_segmentos) == set(segm_ids):
            selected_segmentos = []
        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)
        # --- NOVA QUERY AGREGADA ---
        df = get_dados_agrupados(
            group_fields=['ano'],
            anos=selected_years,
            meses=selected_months,
            tipos_atendimento=selected_tipos_atendimento,
            formas_pagamento=selected_pagamentos,
            profissionais=selected_profissionais,
            segmentos=selected_segmentos,
            data_inicial=data_inicial_iso,
            data_final=data_final_iso,
            agregacoes={'valor_total_unico': 'SUM', 'item': 'COUNT'}
        )
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="Sem dados para exibir")
            return fig
        df = df.sort_values('ano')
        anos = [str(int(ano)) for ano in df['ano']]
        y_vals = [v / t if t > 0 else 0 for v, t in zip(df['valor_total_unico_sum'], df['item_count'])]
        percentuais = [None]
        for i in range(1, len(y_vals)):
            prev = y_vals[i-1]
            curr = y_vals[i]
            if prev == 0:
                percentuais.append(None)
            else:
                percentuais.append((curr - prev) / prev * 100)
        textos = []
        text_colors = []
        for i, val in enumerate(y_vals):
            ticket = round(val)
            ticket_str = f"R$ {ticket:,}".replace(",", ".")
            if percentuais[i] is None:
                textos.append(ticket_str)
                text_colors.append('deeppink')
            else:
                perc = percentuais[i]
                sinal = '+' if perc >= 0 else ''
                perc_str = f'({sinal}{perc:.1f}%)'
                textos.append(f'{ticket_str} {perc_str}')
                text_colors.append('green' if perc > 0 else 'red')
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=anos,
            y=y_vals,
            mode='lines+markers+text',
            name='Ticket Médio por Procedimento',
            text=textos,
            textposition='top center',
            textfont=dict(size=14, color=text_colors)
        ))
        fig.update_xaxes(type='category')
        theme_settings_no_yaxis_margin = {k: v for k, v in theme_settings.items() if k not in ['yaxis', 'yaxis2', 'margin']}
        fig.update_layout(
            **theme_settings_no_yaxis_margin,
            xaxis_title="Ano",
            yaxis=dict(
                title="Ticket Médio por Procedimento (R$)",
                tickfont=dict(color="#007bff"),
                side="left"
            ),
            legend_title="Ticket Médio por Procedimento",
            margin=dict(t=60, l=60, r=60, b=60)
        )
        fig.update_yaxes(showgrid=False)
        color_axes = '#000' if theme_toggle else '#90EE90'
        fig.update_xaxes(color=color_axes)
        fig.update_yaxes(color=color_axes)
        fig.update_layout(title_font_color=color_axes)
        fig.update_xaxes(showline=True, linecolor=color_axes)
        fig.update_yaxes(showline=True, linecolor=color_axes)
        return fig
    except Exception as e:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.update_layout(title=f"Erro: {str(e)}")
        return fig

@log_tempo_callback
def update_producao_bruta_por_ano(
    year_values, month_values,
    tipo_atendimento_values, pagamento_values,
    profissional_values, segmento_values,
    todos_anos, todos_meses,
    todos_tipos_atendimento, todos_pagamentos,
    todos_profissionais, todos_segmentos,
    data_inicial, data_final,
    theme_toggle
):
    try:
        from dash import ctx
        import pandas as pd
        import plotly.graph_objects as go
        from database.queries import get_dados_agrupados
        theme_settings = get_graph_theme_settings(theme_toggle)
        years = get_years()
        if todos_anos:
            selected_years = [str(year) for year in years]
        else:
            if year_values is None:
                selected_years = []
            else:
                selected_years = [str(year) for year, checked in zip(years, year_values) if checked]
        esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
        selected_tipos_atendimento = [esp_id for esp_id, checked in zip(esp_ids, tipo_atendimento_values) if checked]
        pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
        selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
        prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
        selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]
        if set(selected_years) == set([str(year) for year in years]):
            selected_years = []
        if set(selected_tipos_atendimento) == set(esp_ids):
            selected_tipos_atendimento = []
        if set(selected_pagamentos) == set(pag_ids):
            selected_pagamentos = []
        if set(selected_profissionais) == set(prof_ids):
            selected_profissionais = []
        if set(selected_segmentos) == set(segm_ids):
            selected_segmentos = []
        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)
        # --- NOVA QUERY AGREGADA ---
        df = get_dados_agrupados(
            group_fields=['ano'],
            anos=selected_years,
            tipos_atendimento=selected_tipos_atendimento,
            formas_pagamento=selected_pagamentos,
            profissionais=selected_profissionais,
            segmentos=selected_segmentos,
            data_inicial=data_inicial_iso,
            data_final=data_final_iso,
            agregacoes={'valor_total_unico': 'SUM', 'codigo_atendimento': 'COUNT(DISTINCT)'}
        )
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="Sem dados para exibir")
            return fig
        df = df.sort_values('ano')
        anos = [str(int(ano)) for ano in df['ano']]
        totais = df['valor_total_unico_sum'].tolist()
        percentuais = [None]
        for i in range(1, len(totais)):
            if totais[i-1] == 0:
                percentuais.append(None)
            else:
                percentuais.append((totais[i] - totais[i-1]) / totais[i-1] * 100)
        texts = []
        text_colors = []
        for i, total in enumerate(totais):
            txt = f"R$ {total:,.2f}".replace(",", ".")
            if percentuais[i] is not None:
                perc = percentuais[i]
                sinal = '+' if perc > 0 else ''
                txt += f" ({sinal}{perc:.1f}%)"
                text_colors.append('green' if perc > 0 else 'red')
            else:
                text_colors.append('deeppink')
            texts.append(txt)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=anos,
            y=totais,
            mode='lines+markers+text',
            name='Produção Bruta',
            text=texts,
            textposition='top center',
            textfont=dict(size=14, color=text_colors),
            line=dict(color='#007bff', width=3),
            marker=dict(size=10, color='#007bff')
        ))
        theme_settings_no_yaxis_margin = {k: v for k, v in theme_settings.items() if k not in ['yaxis', 'yaxis2', 'margin']}
        fig.update_layout(
            **theme_settings_no_yaxis_margin,
            xaxis_title="Ano",
            yaxis=dict(
                title="Valor da Produção Bruta (R$)",
                tickfont=dict(color="#007bff"),
                side="left"
            ),
            showlegend=False,
            margin=dict(t=60, l=60, r=60, b=60)
        )
        fig.update_xaxes(type='category')
        fig.update_yaxes(tickformat=",.0f", separatethousands=True)
        fig.update_yaxes(showgrid=False)
        color_axes = '#000' if theme_toggle else '#90EE90'
        fig.update_xaxes(color=color_axes)
        fig.update_yaxes(color=color_axes)
        fig.update_layout(title_font_color=color_axes)
        fig.update_xaxes(showline=True, linecolor=color_axes)
        fig.update_yaxes(showline=True, linecolor=color_axes)
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.update_layout(title=f"Erro: {str(e)}")
        return fig

@log_tempo_callback
def update_producao_bruta_mensal(
    year_values, month_values,
    tipo_atendimento_values, pagamento_values,
    profissional_values, segmento_values,
    todos_anos, todos_meses,
    todos_tipos_atendimento, todos_pagamentos,
    todos_profissionais, todos_segmentos,
    data_inicial, data_final,
    theme_toggle
):
    try:
        from dash import ctx
        import pandas as pd
        import plotly.graph_objects as go
        from database.queries import get_dados_agrupados
        theme_settings = get_graph_theme_settings(theme_toggle)
        years = get_years()
        t0 = time.time()
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
        esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
        selected_tipos_atendimento = [esp_id for esp_id, checked in zip(esp_ids, tipo_atendimento_values) if checked]
        pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
        selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
        prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
        selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]
        if set(selected_years) == set([str(year) for year in years]):
            selected_years = []
        if set(selected_months) == set([str(month) for month in range(1, 13)]):
            selected_months = []
        if set(selected_tipos_atendimento) == set(esp_ids):
            selected_tipos_atendimento = []
        if set(selected_pagamentos) == set(pag_ids):
            selected_pagamentos = []
        if set(selected_profissionais) == set(prof_ids):
            selected_profissionais = []
        if set(selected_segmentos) == set(segm_ids):
            selected_segmentos = []
        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)
        # --- NOVA QUERY AGREGADA ---
        df = get_dados_agrupados(
            group_fields=['ano', 'mes'],
            anos=selected_years,
            meses=selected_months,
            tipos_atendimento=selected_tipos_atendimento,
            formas_pagamento=selected_pagamentos,
            profissionais=selected_profissionais,
            segmentos=selected_segmentos,
            data_inicial=data_inicial_iso,
            data_final=data_final_iso,
            agregacoes={'valor_total_unico': 'SUM'}
        )
        t1 = time.time(); print(f'[TIMER] Query get_dados_agrupados: {t1-t0:.3f}s, Linhas: {len(df)}')
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="Sem dados para exibir")
            return fig
        t2 = time.time()
        nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        df['mes_ano'] = df.apply(lambda row: f"{nomes_meses[int(row['mes'])-1]}/{int(row['ano'])}", axis=1)
        df = df.sort_values(['ano', 'mes'])
        x_labels = df['mes_ano'].tolist()
        valores = df['valor_total_unico_sum'].tolist()
        media = sum(valores) / len([v for v in valores if v > 0]) if any(v > 0 for v in valores) else 0
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x_labels,
            y=valores,
            name='Valor da Produção Bruta',
            marker_color='#007bff',
            text=[f"R$ {v:,.2f}".replace(",", ".") for v in valores],
            textposition='outside'
        ))
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=[media]*len(x_labels),
            name='Média dos meses exibidos',
            mode='lines',
            line=dict(color='#ff7f0e', width=3, dash='dash')
        ))
        theme_settings_no_yaxis_margin = {k: v for k, v in theme_settings.items() if k not in ['yaxis', 'yaxis2', 'margin']}
        fig.update_layout(
            **theme_settings_no_yaxis_margin,
            xaxis_title="Mês/Ano",
            yaxis=dict(
                title="Valor da Produção Bruta (R$)",
                tickfont=dict(color="#007bff"),
                side="left"
            ),
            showlegend=False,
            margin=dict(t=60, l=60, r=60, b=60)
        )
        fig.update_xaxes(type='category')
        fig.update_yaxes(tickformat=".2f")
        t5 = time.time(); print(f'[TIMER] plotly: {t5-t2:.3f}s')
        fig.update_yaxes(showgrid=False)
        color_axes = '#000' if theme_toggle else '#90EE90'
        fig.update_xaxes(color=color_axes)
        fig.update_yaxes(color=color_axes)
        fig.update_layout(title_font_color=color_axes)
        fig.update_xaxes(showline=True, linecolor=color_axes)
        fig.update_yaxes(showline=True, linecolor=color_axes)
        return fig
    except Exception as e:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.update_layout(title=f"Erro: {str(e)}")
        return fig

@callback(
    Output('ticket-medio-por-procedimento-ano', 'figure'),
    [
        Input('dados-filtrados-store', 'data'),
        Input(ThemeSwitchAIO.ids.switch("theme"), 'value')
    ]
)
def update_ticket_medio_por_procedimento_ano(dados_filtrados_json, theme_toggle):
    import pandas as pd
    import plotly.graph_objects as go
    if not dados_filtrados_json:
        return go.Figure()
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return go.Figure()
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year.astype(int)
    df_group = df.groupby('ano', as_index=False).agg(
        valor_total=('valor_total_unico', 'sum'),
        procedimentos=('item', 'count')
    )
    df_group = df_group.sort_values('ano')
    anos = df_group['ano'].astype(str).tolist()
    y_vals = [v / t if t > 0 else 0 for v, t in zip(df_group['valor_total'], df_group['procedimentos'])]
    textos = []
    text_colors = []
    for i, val in enumerate(y_vals):
        ticket = round(val)
        ticket_str = f"R$ {ticket:,}".replace(",", ".")
        if i == 0:
            textos.append(ticket_str)
            text_colors.append('deeppink')
        else:
            prev = y_vals[i-1]
            if prev == 0:
                textos.append(ticket_str)
                text_colors.append('deeppink')
            else:
                perc = (val - prev) / prev * 100
                sinal = '+' if perc >= 0 else ''
                perc_str = f'({sinal}{perc:.1f}%)'
                cor = 'green' if perc > 0 else 'red'
                textos.append(f'{ticket_str} {perc_str}')
                text_colors.append(cor)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=anos,
        y=y_vals,
        mode='lines+markers+text',
        name='Ticket Médio por Procedimento',
        text=textos,
        textposition='top center',
        textfont=dict(size=14, color=text_colors),
        line=dict(color='#007bff', width=3),
        marker=dict(size=10, color='#007bff')
    ))
    fig.update_xaxes(type='category')
    y_max = max(y_vals) if y_vals else 1
    fig.update_layout(title="Ticket Médio por Procedimento por Ano", xaxis_title="Ano", yaxis_title="Ticket Médio por Procedimento (R$)", margin=dict(t=160))
    fig.update_yaxes(showgrid=False, range=[0, y_max * 1.15])
    color_axes = '#000' if theme_toggle else '#90EE90'
    fig.update_xaxes(color=color_axes)
    fig.update_yaxes(color=color_axes)
    fig.update_layout(title_font_color=color_axes)
    fig.update_xaxes(showline=True, linecolor=color_axes)
    fig.update_yaxes(showline=True, linecolor=color_axes)
    return fig

@log_tempo_callback
def update_producao_bruta_mensal(
    year_values, month_values,
    tipo_atendimento_values, pagamento_values,
    profissional_values, segmento_values,
    todos_anos, todos_meses,
    todos_tipos_atendimento, todos_pagamentos,
    todos_profissionais, todos_segmentos,
    data_inicial, data_final,
    theme_toggle
):
    try:
        from dash import ctx
        import pandas as pd
        import plotly.graph_objects as go
        from database.queries import get_dados_agrupados
        theme_settings = get_graph_theme_settings(theme_toggle)
        years = get_years()
        t0 = time.time()
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
        esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
        selected_tipos_atendimento = [esp_id for esp_id, checked in zip(esp_ids, tipo_atendimento_values) if checked]
        pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
        selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
        prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
        selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]
        if set(selected_years) == set([str(year) for year in years]):
            selected_years = []
        if set(selected_months) == set([str(month) for month in range(1, 13)]):
            selected_months = []
        if set(selected_tipos_atendimento) == set(esp_ids):
            selected_tipos_atendimento = []
        if set(selected_pagamentos) == set(pag_ids):
            selected_pagamentos = []
        if set(selected_profissionais) == set(prof_ids):
            selected_profissionais = []
        if set(selected_segmentos) == set(segm_ids):
            selected_segmentos = []
        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)
        # --- NOVA QUERY AGREGADA ---
        df = get_dados_agrupados(
            group_fields=['ano', 'mes'],
            anos=selected_years,
            meses=selected_months,
            tipos_atendimento=selected_tipos_atendimento,
            formas_pagamento=selected_pagamentos,
            profissionais=selected_profissionais,
            segmentos=selected_segmentos,
            data_inicial=data_inicial_iso,
            data_final=data_final_iso,
            agregacoes={'valor_total_unico': 'SUM'}
        )
        t1 = time.time(); print(f'[TIMER] Query get_dados_agrupados: {t1-t0:.3f}s, Linhas: {len(df)}')
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="Sem dados para exibir")
            return fig
        t2 = time.time()
        nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        df['mes_ano'] = df.apply(lambda row: f"{nomes_meses[int(row['mes'])-1]}/{int(row['ano'])}", axis=1)
        df = df.sort_values(['ano', 'mes'])
        x_labels = df['mes_ano'].tolist()
        valores = df['valor_total_unico_sum'].tolist()
        media = sum(valores) / len([v for v in valores if v > 0]) if any(v > 0 for v in valores) else 0
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x_labels,
            y=valores,
            name='Valor da Produção Bruta',
            marker_color='#007bff',
            text=[f"R$ {v:,.2f}".replace(",", ".") for v in valores],
            textposition='outside'
        ))
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=[media]*len(x_labels),
            name='Média dos meses exibidos',
            mode='lines',
            line=dict(color='#ff7f0e', width=3, dash='dash')
        ))
        theme_settings_no_yaxis_margin = {k: v for k, v in theme_settings.items() if k not in ['yaxis', 'yaxis2', 'margin']}
        fig.update_layout(
            **theme_settings_no_yaxis_margin,
            xaxis_title="Mês/Ano",
            yaxis=dict(
                title="Valor da Produção Bruta (R$)",
                tickfont=dict(color="#007bff"),
                side="left"
            ),
            showlegend=False,
            margin=dict(t=60, l=60, r=60, b=60)
        )
        fig.update_xaxes(type='category')
        fig.update_yaxes(tickformat=".2f")
        fig.update_yaxes(showgrid=False)
        color_axes = '#000' if theme_toggle else '#90EE90'
        fig.update_xaxes(color=color_axes)
        fig.update_yaxes(color=color_axes)
        fig.update_layout(title_font_color=color_axes)
        fig.update_xaxes(showline=True, linecolor=color_axes)
        fig.update_yaxes(showline=True, linecolor=color_axes)
        return fig
    except Exception as e:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.update_layout(title=f"Erro: {str(e)}")
        return fig

@log_tempo_callback
def update_grafico_relacao_procedimentos_por_atendimento_ano(
    year_values, month_values,
    tipo_atendimento_values, pagamento_values,
    profissional_values, segmento_values,
    todos_anos, todos_meses,
    todos_tipos_atendimento, todos_pagamentos,
    todos_profissionais, todos_segmentos,
    data_inicial, data_final,
    theme_toggle
):
    try:
        from dash import ctx
        import pandas as pd
        import plotly.graph_objects as go
        from database.queries import get_dados_agrupados
        theme_settings = get_graph_theme_settings(theme_toggle)
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
        esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
        selected_tipos_atendimento = [esp_id for esp_id, checked in zip(esp_ids, tipo_atendimento_values) if checked]
        pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
        selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
        prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
        selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]
        if set(selected_years) == set([str(year) for year in years]):
            selected_years = []
        if set(selected_months) == set([str(month) for month in range(1, 13)]):
            selected_months = []
        if set(selected_tipos_atendimento) == set(esp_ids):
            selected_tipos_atendimento = []
        if set(selected_pagamentos) == set(pag_ids):
            selected_pagamentos = []
        if set(selected_profissionais) == set(prof_ids):
            selected_profissionais = []
        if set(selected_segmentos) == set(segm_ids):
            selected_segmentos = []
        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)
        # --- NOVA QUERY AGREGADA ---
        df = get_dados_agrupados(
            group_fields=['ano'],
            anos=selected_years,
            meses=selected_months,
            tipos_atendimento=selected_tipos_atendimento,
            formas_pagamento=selected_pagamentos,
            profissionais=selected_profissionais,
            segmentos=selected_segmentos,
            data_inicial=data_inicial_iso,
            data_final=data_final_iso,
            agregacoes={'item': 'COUNT', 'codigo_atendimento': 'COUNT(DISTINCT)'}
        )
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="Sem dados para exibir")
            return fig
        df = df.sort_values('ano')
        anos = [str(int(ano)) for ano in df['ano']]
        relacao = [p / a if a > 0 else 0 for p, a in zip(df['item_count'], df['codigo_atendimento_count_distinct'])]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=anos,
            y=relacao,
            name='Relação Procedimentos/Atendimento',
            mode='lines+markers+text',
            text=[f"{v:.2f}" for v in relacao],
            textposition='top center',
            line=dict(color='#007bff', width=3),
            marker=dict(size=10, color='#007bff')
        ))
        theme_settings_no_yaxis_margin = {k: v for k, v in theme_settings.items() if k not in ['yaxis', 'yaxis2', 'margin']}
        fig.update_layout(
            **theme_settings_no_yaxis_margin,
            xaxis_title="Ano",
            yaxis=dict(
                title="Qtde de Procedimentos / Atendimento",
                tickfont=dict(color="#007bff"),
                side="left"
            ),
            showlegend=False,
            margin=dict(t=60, l=60, r=60, b=60)
        )
        fig.update_xaxes(type='category')
        fig.update_yaxes(tickformat=".2f")
        fig.update_yaxes(showgrid=False)
        color_axes = '#000' if theme_toggle else '#90EE90'
        fig.update_xaxes(color=color_axes)
        fig.update_yaxes(color=color_axes)
        fig.update_layout(title_font_color=color_axes)
        fig.update_xaxes(showline=True, linecolor=color_axes)
        fig.update_yaxes(showline=True, linecolor=color_axes)
        return fig
    except Exception as e:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.update_layout(title=f"Erro: {str(e)}")
        return fig

@callback(
    Output('grid-relacao-procedimentos-por-atendimento-por-medico-ano', 'children'),
    [Input('dados-filtrados-store', 'data')]
)
def update_grid_relacao_procedimentos_por_atendimento_por_medico_ano(dados_filtrados_json):
    import pandas as pd
    from dash import dash_table
    import io
    if not dados_filtrados_json:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year
    # Agrupar por médico e ano
    df_group = df.groupby(['profissional', 'ano']).agg(
        total_procedimentos=('item', 'count'),
        total_atendimentos=('codigo_atendimento', pd.Series.nunique)
    ).reset_index()
    anos = sorted(df_group['ano'].unique())
    medicos = sorted(df_group['profissional'].unique())
    tabela = []
    for medico in medicos:
        linha = {'Médico': medico}
        total_proc_medico = 0
        total_atend_medico = 0
        for ano in anos:
            sub = df_group[(df_group['profissional'] == medico) & (df_group['ano'] == ano)]
            if not sub.empty and sub.iloc[0]['total_atendimentos'] > 0:
                relacao = sub.iloc[0]['total_procedimentos'] / sub.iloc[0]['total_atendimentos']
                total_proc_medico += sub.iloc[0]['total_procedimentos']
                total_atend_medico += sub.iloc[0]['total_atendimentos']
            else:
                relacao = 0
            linha[str(ano)] = relacao
        linha['Total Geral'] = total_proc_medico / total_atend_medico if total_atend_medico > 0 else 0
        tabela.append(linha)
    # Calcular totais da última linha (por ano)
    total_geral_linha = {'Médico': 'Total Geral'}
    total_proc_ano = {}
    total_atend_ano = {}
    for ano in anos:
        total_proc = df_group[df_group['ano'] == ano]['total_procedimentos'].sum()
        total_atend = df_group[df_group['ano'] == ano]['total_atendimentos'].sum()
        total_proc_ano[ano] = total_proc
        total_atend_ano[ano] = total_atend
        total_geral_linha[str(ano)] = total_proc / total_atend if total_atend > 0 else 0
    # Calcular total geral (canto inferior direito)
    total_proc_geral = sum(total_proc_ano.values())
    total_atend_geral = sum(total_atend_ano.values())
    total_geral_linha['Total Geral'] = total_proc_geral / total_atend_geral if total_atend_geral > 0 else 0
    tabela.append(total_geral_linha)
    columns = [{'name': 'Qtde de Procedimentos / Atendimento', 'id': 'Médico'}]
    columns += [{'name': str(ano), 'id': str(ano)} for ano in anos]
    columns += [{'name': 'Total Geral', 'id': 'Total Geral'}]
    # Formatar valores (1 casa decimal)
    for linha in tabela:
        for ano in anos:
            linha[str(ano)] = f"{linha[str(ano)]:,.1f}".replace(",", ".")
        if 'Total Geral' in linha:
            linha['Total Geral'] = f"{linha['Total Geral']:,.1f}".replace(",", ".")
    return dash_table.DataTable(
        columns=columns,
        data=tabela,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
        style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{Médico} = "Total Geral"'},
                'backgroundColor': '#888',
                'color': 'white'
            }
        ]
    )

@callback(
    Output('grafico-ticket-medio-vs-quantidade-atendimentos-ano', 'figure'),
    [Input('dados-filtrados-store', 'data'),
     Input(ThemeSwitchAIO.ids.switch("theme"), 'value')]
)
def update_grafico_ticket_medio_vs_quantidade_atendimentos_ano(dados_filtrados_json, theme_toggle):
    import pandas as pd
    import plotly.graph_objects as go
    import io
    if not dados_filtrados_json:
        return go.Figure()
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return go.Figure()
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year.astype(int)
    df_group = df.groupby('ano', as_index=False).agg(
        atendimentos=('codigo_atendimento', pd.Series.nunique),
        valor_total=('valor_total_unico', 'sum')
    )
    df_group = df_group.sort_values('ano')
    anos = df_group['ano'].astype(str).tolist()
    qtd_atendimentos = df_group['atendimentos'].tolist()
    ticket_medio = [v / a if a > 0 else 0 for v, a in zip(df_group['valor_total'], df_group['atendimentos'])]
    fig = go.Figure()
    # Texto para Quantidade de Atendimentos
    textos_atend = [f"{v:,}".replace(",", ".") for v in qtd_atendimentos]
    # Texto para Ticket Médio
    textos_ticket = [f"R$ {v:,.2f}".replace(",", ".") for v in ticket_medio]
    # Linha 1: Quantidade de atendimentos (eixo Y1)
    fig.add_trace(go.Scatter(
        x=anos,
        y=qtd_atendimentos,
        name='Quantidade de Atendimentos',
        mode='lines+markers+text',
        line=dict(color='#007bff', width=3),
        marker=dict(size=10, color='#007bff'),
        yaxis='y1',
        text=textos_atend,
        textposition='top center',
        textfont=dict(size=14, color='#007bff')
    ))
    # Linha 2: Ticket médio (eixo Y2)
    fig.add_trace(go.Scatter(
        x=anos,
        y=ticket_medio,
        name='Ticket Médio',
        mode='lines+markers+text',
        line=dict(color='#ff7f0e', width=3, dash='dash'),
        marker=dict(size=10, color='#ff7f0e'),
        yaxis='y2',
        text=textos_ticket,
        textposition='bottom center',
        textfont=dict(size=14, color='#ff7f0e')
    ))
    # Ajuste o topo do gráfico para não cortar textos
    y1_max = max(qtd_atendimentos) if qtd_atendimentos else 1
    y2_max = max(ticket_medio) if ticket_medio else 1
    fig.update_layout(
        xaxis_title="Ano",
        yaxis=dict(
            title="Quantidade de Atendimentos",
            tickfont=dict(color="#007bff"),
            side="left",
            range=[0, y1_max * 1.25]
        ),
        yaxis2=dict(
            title="Ticket Médio (R$)",
            tickfont=dict(color="#ff7f0e"),
            overlaying="y",
            side="right",
            range=[0, y2_max * 1.25]
        ),
        legend=dict(x=1, y=1, xanchor='right', yanchor='top', orientation='h'),
        margin=dict(t=200, l=60, r=60, b=60),
        title="Ticket Médio vs Quantidade de Atendimentos por Ano"
    )
    fig.update_xaxes(type='category')
    fig.update_yaxes(showgrid=False)
    color_axes = '#000' if theme_toggle else '#90EE90'
    fig.update_xaxes(color=color_axes)
    fig.update_yaxes(color=color_axes)
    fig.update_layout(title_font_color=color_axes)
    fig.update_xaxes(showline=True, linecolor=color_axes)
    fig.update_yaxes(showline=True, linecolor=color_axes)
    return fig

@log_tempo_callback
def update_grid_producao_bruta_por_medico_ano(
    year_values, month_values,
    tipo_atendimento_values, pagamento_values,
    profissional_values, segmento_values,
    todos_anos, todos_meses,
    todos_tipos_atendimento, todos_pagamentos,
    todos_profissionais, todos_segmentos,
    data_inicial, data_final,
    theme_toggle
):
    try:
        from dash import ctx
        import pandas as pd
        from dash import dash_table
        from database.queries import get_dados_agrupados
        theme_settings = get_graph_theme_settings(theme_toggle)
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
        esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
        selected_tipos_atendimento = [esp_id for esp_id, checked in zip(esp_ids, tipo_atendimento_values) if checked]
        pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
        selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
        prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
        selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]
        if set(selected_years) == set([str(year) for year in years]):
            selected_years = []
        if set(selected_months) == set([str(month) for month in range(1, 13)]):
            selected_months = []
        if set(selected_tipos_atendimento) == set(esp_ids):
            selected_tipos_atendimento = []
        if set(selected_pagamentos) == set(pag_ids):
            selected_pagamentos = []
        if set(selected_profissionais) == set(prof_ids):
            selected_profissionais = []
        if set(selected_segmentos) == set(segm_ids):
            selected_segmentos = []
        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)
        # --- NOVA QUERY AGREGADA ---
        df = get_dados_agrupados(
            group_fields=['profissional', 'ano'],
            anos=selected_years,
            meses=selected_months,
            tipos_atendimento=selected_tipos_atendimento,
            formas_pagamento=selected_pagamentos,
            profissionais=selected_profissionais,
            segmentos=selected_segmentos,
            data_inicial=data_inicial_iso,
            data_final=data_final_iso,
            agregacoes={'valor_total_unico': 'SUM'}
        )
        if df.empty:
            return dash_table.DataTable(
                columns=[{"name": "", "id": "vazio"}],
                data=[],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
                style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'}
            )
        anos = sorted(df['ano'].unique())
        medicos = sorted(df['profissional'].unique())
        tabela = []
        for medico in medicos:
            linha = {'Médico': medico}
            total_valor_medico = 0
            for ano in anos:
                valor = df[(df['profissional'] == medico) & (df['ano'] == ano)]['valor_total_unico_sum'].sum()
                linha[str(ano)] = valor
                total_valor_medico += valor
            linha['Total Geral'] = total_valor_medico
            tabela.append(linha)
        total_geral_linha = {'Médico': 'Total Geral'}
        for ano in anos:
            total_geral_linha[str(ano)] = sum(linha[str(ano)] for linha in tabela)
        total_geral_linha['Total Geral'] = sum(linha['Total Geral'] for linha in tabela)
        tabela.append(total_geral_linha)
        columns = [{'name': 'Valor da Produção Bruta (R$)', 'id': 'Médico'}]
        columns += [{'name': str(ano), 'id': str(ano)} for ano in anos]
        columns += [{'name': 'Total Geral', 'id': 'Total Geral'}]
        for linha in tabela:
            for ano in anos:
                linha[str(ano)] = f"R$ {linha[str(ano)]:,.2f}".replace(",", ".")
            if 'Total Geral' in linha:
                linha['Total Geral'] = f"R$ {linha['Total Geral']:,.2f}".replace(",", ".")
        return dash_table.DataTable(
            columns=columns,
            data=tabela,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
            style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{Médico} = "Total Geral"'},
                    'backgroundColor': '#888',
                    'color': 'white'
                }
            ]
        )
    except Exception as e:
        from dash import html
        return html.Div(f"Erro: {str(e)}")

@log_tempo_callback
def update_grid_procedimentos_por_medico_ano(
    year_values, month_values,
    tipo_atendimento_values, pagamento_values,
    profissional_values, segmento_values,
    todos_anos, todos_meses,
    todos_tipos_atendimento, todos_pagamentos,
    todos_profissionais, todos_segmentos,
    data_inicial, data_final,
    theme_toggle
):
    try:
        from dash import ctx
        import pandas as pd
        from dash import dash_table
        from database.queries import get_dados_agrupados
        theme_settings = get_graph_theme_settings(theme_toggle)
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
        esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
        selected_tipos_atendimento = [esp_id for esp_id, checked in zip(esp_ids, tipo_atendimento_values) if checked]
        pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
        selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
        prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
        selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]
        if set(selected_years) == set([str(year) for year in years]):
            selected_years = []
        if set(selected_months) == set([str(month) for month in range(1, 13)]):
            selected_months = []
        if set(selected_tipos_atendimento) == set(esp_ids):
            selected_tipos_atendimento = []
        if set(selected_pagamentos) == set(pag_ids):
            selected_pagamentos = []
        if set(selected_profissionais) == set(prof_ids):
            selected_profissionais = []
        if set(selected_segmentos) == set(segm_ids):
            selected_segmentos = []
        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)
        # --- NOVA QUERY AGREGADA ---
        df = get_dados_agrupados(
            group_fields=['profissional', 'ano'],
            anos=selected_years,
            meses=selected_months,
            tipos_atendimento=selected_tipos_atendimento,
            formas_pagamento=selected_pagamentos,
            profissionais=selected_profissionais,
            segmentos=selected_segmentos,
            data_inicial=data_inicial_iso,
            data_final=data_final_iso,
            agregacoes={'item': 'COUNT', 'tipo_atendimento': 'COUNT(DISTINCT)'}
        )
        if df.empty:
            return dash_table.DataTable(
                columns=[{"name": "", "id": "vazio"}],
                data=[],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
                style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'}
            )
        anos = sorted(df['ano'].unique())
        medicos = sorted(df['profissional'].unique())
        tabela = []
        for medico in medicos:
            linha = {'Médico': medico}
            total_geral = 0
            for ano in anos:
                valor = df[(df['profissional'] == medico) & (df['ano'] == ano)]['item_count'].sum()
                linha[str(ano)] = valor
                total_geral += valor
            linha['Total Geral'] = total_geral
            tabela.append(linha)
        total_geral_linha = {'Médico': 'Total Geral'}
        for ano in anos:
            total_geral_linha[str(ano)] = sum(linha[str(ano)] for linha in tabela)
        total_geral_linha['Total Geral'] = sum(linha['Total Geral'] for linha in tabela)
        tabela.append(total_geral_linha)
        columns = [{'name': 'Quantidade de Procedimentos', 'id': 'Médico'}]
        columns += [{'name': str(ano), 'id': str(ano)} for ano in anos]
        columns += [{'name': 'Total Geral', 'id': 'Total Geral'}]
        for linha in tabela:
            for ano in anos:
                linha[str(ano)] = f"{linha[str(ano)]:,.0f}".replace(",", ".")
            linha['Total Geral'] = f"{linha['Total Geral']:,.0f}".replace(",", ".")
        return dash_table.DataTable(
            columns=columns,
            data=tabela,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
            style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{Médico} = "Total Geral"'},
                    'backgroundColor': '#888',
                    'color': 'white'
                }
            ]
        )
    except Exception as e:
        return f"Erro: {str(e)}"

@log_tempo_callback
def update_grid_ticket_medio_por_medico_ano(
    year_values, month_values,
    tipo_atendimento_values, pagamento_values,
    profissional_values, segmento_values,
    todos_anos, todos_meses,
    todos_tipos_atendimento, todos_pagamentos,
    todos_profissionais, todos_segmentos,
    data_inicial, data_final,
    theme_toggle
):
    try:
        from dash import ctx
        import pandas as pd
        from dash import dash_table
        from database.queries import get_dados_agrupados
        theme_settings = get_graph_theme_settings(theme_toggle)
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
        esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
        selected_tipos_atendimento = [esp_id for esp_id, checked in zip(esp_ids, tipo_atendimento_values) if checked]
        pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
        selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
        prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
        selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]
        if set(selected_years) == set([str(year) for year in years]):
            selected_years = []
        if set(selected_months) == set([str(month) for month in range(1, 13)]):
            selected_months = []
        if set(selected_tipos_atendimento) == set(esp_ids):
            selected_tipos_atendimento = []
        if set(selected_pagamentos) == set(pag_ids):
            selected_pagamentos = []
        if set(selected_profissionais) == set(prof_ids):
            selected_profissionais = []
        if set(selected_segmentos) == set(segm_ids):
            selected_segmentos = []
        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)
        # --- NOVA QUERY AGREGADA ---
        df = get_dados_agrupados(
            group_fields=['profissional', 'ano'],
            anos=selected_years,
            meses=selected_months,
            tipos_atendimento=selected_tipos_atendimento,
            formas_pagamento=selected_pagamentos,
            profissionais=selected_profissionais,
            segmentos=selected_segmentos,
            data_inicial=data_inicial_iso,
            data_final=data_final_iso,
            agregacoes={'valor_total_unico': 'SUM', 'codigo_atendimento': 'COUNT(DISTINCT)'}
        )
        if df.empty:
            return dash_table.DataTable(
                columns=[{"name": "", "id": "vazio"}],
                data=[],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
                style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'}
            )
        anos = sorted(df['ano'].unique())
        medicos = sorted(df['profissional'].unique())
        tabela = []
        for medico in medicos:
            linha = {'Médico': medico}
            total_valor_medico = 0
            total_atendimentos_medico = 0
            for ano in anos:
                sub = df[(df['profissional'] == medico) & (df['ano'] == ano)]
                if not sub.empty and sub.iloc[0]['codigo_atendimento_count_distinct'] > 0:
                    ticket = round(sub.iloc[0]['valor_total_unico_sum'] / sub.iloc[0]['codigo_atendimento_count_distinct'])
                    total_valor_medico += sub.iloc[0]['valor_total_unico_sum']
                    total_atendimentos_medico += sub.iloc[0]['codigo_atendimento_count_distinct']
                else:
                    ticket = 0
                linha[str(ano)] = ticket
            linha['Total Geral'] = round(total_valor_medico / total_atendimentos_medico) if total_atendimentos_medico > 0 else 0
            tabela.append(linha)
        total_geral_linha = {'Médico': 'Total Geral'}
        total_valor_ano = {}
        total_atendimentos_ano = {}
        for ano in anos:
            total_valor = df[df['ano'] == ano]['valor_total_unico_sum'].sum()
            total_atend = df[df['ano'] == ano]['codigo_atendimento_count_distinct'].sum()
            total_valor_ano[ano] = total_valor
            total_atendimentos_ano[ano] = total_atend
            total_geral_linha[str(ano)] = round(total_valor / total_atend) if total_atend > 0 else 0
        total_valor_geral = sum(total_valor_ano.values())
        total_atend_geral = sum(total_atendimentos_ano.values())
        total_geral_linha['Total Geral'] = round(total_valor_geral / total_atend_geral) if total_atend_geral > 0 else 0
        tabela.append(total_geral_linha)
        columns = [{'name': 'Ticket Médio / Atendimento (R$)', 'id': 'Médico'}]
        columns += [{'name': str(ano), 'id': str(ano)} for ano in anos]
        columns += [{'name': 'Total Geral', 'id': 'Total Geral'}]
        for linha in tabela:
            for ano in anos:
                linha[str(ano)] = f"{linha[str(ano)]:,.0f}".replace(",", ".")
            if 'Total Geral' in linha:
                linha['Total Geral'] = f"{linha['Total Geral']:,.0f}".replace(",", ".")
        return dash_table.DataTable(
            columns=columns,
            data=tabela,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
            style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{Médico} = "Total Geral"'},
                    'backgroundColor': '#888',
                    'color': 'white'
                }
            ]
        )
    except Exception as e:
        return f"Erro: {str(e)}"

# 1. Valor da Produção Bruta (R$) / Média dos meses selecionados
def get_selected_filters(ctx, year_values, month_values, tipo_atendimento_values, pagamento_values, profissional_values, segmento_values, todos_anos, todos_meses, todos_tipos_atendimento, todos_pagamentos, todos_profissionais, todos_segmentos, segmentos_selecoes_store=None):
    years = get_years()
    if todos_anos:
        selected_years = [str(year) for year in years]
    else:
        selected_years = [str(year) for year, checked in zip(years, year_values) if checked] if year_values else []
    if todos_meses:
        selected_months = [str(month) for month in range(1, 13)]
    else:
        selected_months = [str(month) for month, checked in zip(range(1, 13), month_values) if checked] if month_values else []
    # Mapear os IDs sanitizados de tipo_atendimento de volta para os nomes reais
    from database.queries import get_tipos_atendimento
    tipos_atendimento = get_tipos_atendimento()
    id_to_nome = {sanitize_id(item['nome']): item['nome'] for item in tipos_atendimento}
    esp_ids = [item["id"]["index"] for item in ctx.inputs_list[2]]
    selected_tipos_atendimento = [id_to_nome[esp_id] for esp_id, checked in zip(esp_ids, tipo_atendimento_values) if checked and esp_id in id_to_nome]
    pag_ids = [item["id"]["index"] for item in ctx.inputs_list[3]]
    selected_pagamentos = [pag_id for pag_id, checked in zip(pag_ids, pagamento_values) if checked]
    prof_ids = [item["id"]["index"] for item in ctx.inputs_list[4]]
    selected_profissionais = [prof_id for prof_id, checked in zip(prof_ids, profissional_values) if checked]
    # SEGMENTOS: usar o store de seleções se fornecido
    if segmentos_selecoes_store is not None:
        segmentos = get_segmentos()
        if not segmentos_selecoes_store or all(segmentos_selecoes_store.get(str(i), True) for i in range(len(segmentos))):
            selected_segmentos = [segmento["nome"] for segmento in segmentos]
        else:
            selected_segmentos = [segmentos[int(idx)]["nome"] for idx, marcado in segmentos_selecoes_store.items() if marcado]
    else:
        segm_ids = [item["id"]["index"] for item in ctx.inputs_list[5]]
        selected_segmentos = [segm_id for segm_id, checked in zip(segm_ids, segmento_values) if checked]
    return selected_years, selected_months, selected_tipos_atendimento, selected_pagamentos, selected_profissionais, selected_segmentos



# 3. Total de Procedimentos por Ano
@callback(
    Output('total-procedimentos-por-ano', 'figure'),
    [Input('dados-filtrados-store', 'data'),
     Input(ThemeSwitchAIO.ids.switch("theme"), 'value')]
)
def update_total_procedimentos_por_ano(dados_filtrados_json, theme_toggle):
    import pandas as pd
    import plotly.graph_objects as go
    if not dados_filtrados_json:
        return go.Figure()
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return go.Figure()
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year.astype(int)
    df_group = df.groupby('ano', as_index=False).agg(total_procedimentos=('item', 'count'))
    anos = df_group['ano'].astype(str).tolist()
    valores = df_group['total_procedimentos'].tolist()
    textos = []
    text_colors = []
    for i, v in enumerate(valores):
        valor_str = f"{v:,}".replace(",", ".")
        if i == 0:
            textos.append(valor_str)
            text_colors.append('deeppink')
        else:
            prev = valores[i-1]
            if prev == 0:
                textos.append(valor_str)
                text_colors.append('deeppink')
            else:
                perc = (v - prev) / prev * 100
                sinal = '+' if perc > 0 else ''
                perc_str = f'({sinal}{perc:.1f}%)'
                cor = 'green' if perc > 0 else 'red'
                textos.append(f'{valor_str} {perc_str}')
                text_colors.append(cor)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=anos,
        y=valores,
        mode='lines+markers+text',
        text=textos,
        textposition='top center',
        textfont=dict(size=14, color=text_colors),
        line=dict(color='#007bff', width=3)
    ))
    y_max = max(valores) if valores else 1
    fig.update_layout(title="Total de Procedimentos por Ano", xaxis_title="Ano", yaxis_title="Total de Procedimentos", margin=dict(t=120))
    fig.update_yaxes(showgrid=False, range=[0, y_max * 1.10])
    color_axes = '#000' if theme_toggle else '#90EE90'
    fig.update_xaxes(color=color_axes)
    fig.update_yaxes(color=color_axes)
    fig.update_layout(title_font_color=color_axes)
    fig.update_xaxes(showline=True, linecolor=color_axes)
    fig.update_yaxes(showline=True, linecolor=color_axes)
    return fig

# 4. Grid: Quantidade de Procedimentos por Médico por Ano
@callback(
    Output('grid-procedimentos-por-medico-ano', 'children'),
    [Input('dados-filtrados-store', 'data')]
)
def update_grid_procedimentos_por_medico_ano(dados_filtrados_json):
    if not dados_filtrados_json:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year
    df_group = df.groupby(['profissional', 'ano']).agg(total_procedimentos=('item', 'count')).reset_index()
    anos = sorted(df_group['ano'].unique())
    medicos = sorted(df_group['profissional'].unique())
    tabela = []
    for medico in medicos:
        linha = {'Médico': medico}
        total_geral = 0
        for ano in anos:
            valor = df_group[(df_group['profissional'] == medico) & (df_group['ano'] == ano)]['total_procedimentos'].sum()
            linha[str(ano)] = valor
            total_geral += valor
        linha['Total Geral'] = total_geral
        tabela.append(linha)
    total_geral_linha = {'Médico': 'Total Geral'}
    for ano in anos:
        total_geral_linha[str(ano)] = sum(linha[str(ano)] for linha in tabela)
    total_geral_linha['Total Geral'] = sum(linha['Total Geral'] for linha in tabela)
    tabela.append(total_geral_linha)
    columns = [{'name': 'Quantidade de Procedimentos', 'id': 'Médico'}]
    columns += [{'name': str(ano), 'id': str(ano)} for ano in anos]
    columns += [{'name': 'Total Geral', 'id': 'Total Geral'}]
    for linha in tabela:
        for ano in anos:
            linha[str(ano)] = f"{linha[str(ano)]:,.0f}".replace(",", ".")
        linha['Total Geral'] = f"{linha['Total Geral']:,.0f}".replace(",", ".")
    return dash_table.DataTable(
        columns=columns,
        data=tabela,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
        style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'}
    )




# --- SUMMARY CARDS (TOTALS) ---
@callback(
    [Output("total-atendimentos", "children"),
     Output("total-procedimentos", "children"),
     Output("valor-total", "children"),
     Output("ticket-medio", "children")],
    [Input('dados-filtrados-store', 'data')]
)
def update_summary_cards(dados_filtrados_json):
    if not dados_filtrados_json:
        return ["0", "0", "R$ 0,00", "R$ 0,00"]
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return ["0", "0", "R$ 0,00", "R$ 0,00"]
    total_atendimentos = df['codigo_atendimento'].nunique()
    total_procedimentos = len(df)
    valor_total = df['valor_total_unico'].sum()
    ticket_medio = valor_total / total_atendimentos if total_atendimentos else 0
    return [
        f"{total_atendimentos:,}".replace(",", "."),
        f"{total_procedimentos:,}".replace(",", "."),
        f"R$ {valor_total:,.2f}".replace(",", "."),
        f"R$ {ticket_medio:,.2f}".replace(",", ".")
    ]

# --- EXAMPLE CHART CALLBACK ---
@callback(
    Output('producao-bruta-por-ano', 'figure'),
    [Input('dados-filtrados-store', 'data'),
     Input(ThemeSwitchAIO.ids.switch("theme"), 'value')]
)
def update_producao_bruta_por_ano(dados_filtrados_json, theme_toggle):
    import pandas as pd
    import plotly.graph_objects as go
    import io
    if not dados_filtrados_json:
        return go.Figure()
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return go.Figure()
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year.astype(int)
    df_group = df.groupby('ano', as_index=False).agg(valor_total=('valor_total_unico', 'sum'))
    anos = df_group['ano'].astype(str).tolist()
    valores = df_group['valor_total'].tolist()
    textos = []
    text_colors = []
    for i, v in enumerate(valores):
        valor_str = f"R$ {v:,.2f}".replace(",", ".")
        if i == 0:
            textos.append(valor_str)
            text_colors.append('deeppink')
        else:
            prev = valores[i-1]
            if prev == 0:
                textos.append(valor_str)
                text_colors.append('deeppink')
            else:
                perc = (v - prev) / prev * 100
                sinal = '+' if perc > 0 else ''
                perc_str = f'({sinal}{perc:.1f}%)'
                cor = 'green' if perc > 0 else 'red'
                textos.append(f'{valor_str} {perc_str}')
                text_colors.append(cor)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=anos,
        y=valores,
        mode='lines+markers+text',
        text=textos,
        textposition='top center',
        textfont=dict(size=14, color=text_colors),
        line=dict(color='#007bff', width=3)
    ))
    y_max = max(valores) if valores else 1
    fig.update_layout(title="Produção Bruta por Ano", margin=dict(t=120))
    fig.update_yaxes(showgrid=False, range=[0, y_max * 1.10])  # 10% acima do maior valor
    fig.update_yaxes(showgrid=False)
    color_axes = '#000' if theme_toggle else '#90EE90'
    fig.update_xaxes(color=color_axes)
    fig.update_yaxes(color=color_axes)
    fig.update_layout(title_font_color=color_axes)
    fig.update_xaxes(showline=True, linecolor=color_axes)
    fig.update_yaxes(showline=True, linecolor=color_axes)
    return fig

# --- REPEAT FOR ALL OTHER CHARTS/GRIDS ---
# For each chart/grid, create a callback with only the store and theme toggle as inputs, load the DataFrame, and perform the necessary aggregation/plotting.
# ... existing code ...

# --- PRODUCAO BRUTA MENSAL ---
@callback(
    Output('producao-bruta-mensal', 'figure'),
    [Input('dados-filtrados-store', 'data'),
     Input(ThemeSwitchAIO.ids.switch("theme"), 'value')]
)
def update_producao_bruta_mensal(dados_filtrados_json, theme_toggle):
    if not dados_filtrados_json:
        return go.Figure()
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return go.Figure()
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year
    df['mes'] = pd.to_datetime(df['data_atendimento']).dt.month
    df_group = df.groupby(['ano', 'mes']).agg(valor_total=('valor_total_unico', 'sum')).reset_index()
    nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    df_group['mes_ano'] = df_group.apply(lambda row: f"{nomes_meses[int(row['mes'])-1]}/{int(row['ano'])}", axis=1)
    df_group = df_group.sort_values(['ano', 'mes'])
    x_labels = df_group['mes_ano'].tolist()
    valores = df_group['valor_total'].tolist()
    media = sum(valores) / len([v for v in valores if v > 0]) if any(v > 0 for v in valores) else 0
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_labels,
        y=valores,
        name='Valor da Produção Bruta',
        marker_color='#007bff',
        text=[f"R$ {v:,.2f}".replace(",", ".") for v in valores],
        textposition='outside'
    ))
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=[media]*len(x_labels),
        name='Média dos meses exibidos',
        mode='lines',
        line=dict(color='#ff7f0e', width=3, dash='dash')
    ))
    fig.update_layout(title="Produção Bruta Mensal")
    fig.update_yaxes(showgrid=False)
    color_axes = '#000' if theme_toggle else '#90EE90'
    fig.update_xaxes(color=color_axes)
    fig.update_yaxes(color=color_axes)
    fig.update_layout(title_font_color=color_axes)
    fig.update_xaxes(showline=True, linecolor=color_axes)
    fig.update_yaxes(showline=True, linecolor=color_axes)
    return fig

# ... existing code ...

# --- Valor da Produção Bruta (R$) por Médico e Ano ---
@callback(
    Output('grid-producao-bruta-por-medico-ano', 'children'),
    [Input('dados-filtrados-store', 'data')]
)
def update_grid_producao_bruta_por_medico_ano(dados_filtrados_json):
    import pandas as pd
    from dash import dash_table
    if not dados_filtrados_json:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year
    df_group = df.groupby(['profissional', 'ano']).agg(valor_total=('valor_total_unico', 'sum')).reset_index()
    anos = sorted(df_group['ano'].unique())
    medicos = sorted(df_group['profissional'].unique())
    tabela = []
    for medico in medicos:
        linha = {'Médico': medico}
        total_valor = 0
        for ano in anos:
            valor = df_group[(df_group['profissional'] == medico) & (df_group['ano'] == ano)]['valor_total'].sum()
            linha[str(ano)] = valor
            total_valor += valor
        linha['Total Geral'] = total_valor
        tabela.append(linha)
    total_geral_linha = {'Médico': 'Total Geral'}
    for ano in anos:
        total_geral_linha[str(ano)] = sum(linha[str(ano)] for linha in tabela)
    total_geral_linha['Total Geral'] = sum(linha['Total Geral'] for linha in tabela)
    tabela.append(total_geral_linha)
    columns = [{'name': 'Valor da Produção Bruta (R$)', 'id': 'Médico'}]
    columns += [{'name': str(ano), 'id': str(ano)} for ano in anos]
    columns += [{'name': 'Total Geral', 'id': 'Total Geral'}]
    for linha in tabela:
        for ano in anos:
            linha[str(ano)] = f"R$ {linha[str(ano)]:,.2f}".replace(",", ".")
        linha['Total Geral'] = f"R$ {linha['Total Geral']:,.2f}".replace(",", ".")
    return dash_table.DataTable(
        columns=columns,
        data=tabela,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
        style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'}
    )

# --- Atendimentos por Médico por Mês ---
@callback(
    Output('atendimentos-por-medico-mensal', 'figure'),
    [Input('dados-filtrados-store', 'data'),
     Input(ThemeSwitchAIO.ids.switch("theme"), 'value')]
)
def update_atendimentos_por_medico_mensal(dados_filtrados_json, theme_toggle):
    import pandas as pd
    import plotly.graph_objects as go
    if not dados_filtrados_json:
        return go.Figure()
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return go.Figure()
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year
    df['mes'] = pd.to_datetime(df['data_atendimento']).dt.month
    df_group = df.groupby(['profissional', 'ano', 'mes']).agg(atendimentos=('codigo_atendimento', pd.Series.nunique)).reset_index()
    nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    # Criar coluna mes_ano para ordenação cronológica
    df_group['mes_ano'] = df_group.apply(lambda row: f"{nomes_meses[int(row['mes'])-1]}/{int(row['ano'])}", axis=1)
    df_group = df_group.sort_values(['ano', 'mes'])
    x_labels = df_group['mes_ano'].unique().tolist()
    fig = go.Figure()
    for medico in sorted(df_group['profissional'].unique()):
        sub = df_group[df_group['profissional'] == medico]
        # Garantir que os dados estejam alinhados com x_labels
        y = [sub[sub['mes_ano'] == x]['atendimentos'].values[0] if x in sub['mes_ano'].values else 0 for x in x_labels]
        fig.add_trace(go.Scatter(x=x_labels, y=y, mode='lines+markers', name=medico))
    fig.update_layout(title="Atendimentos por Médico por Mês", xaxis_title="Mês/Ano", yaxis_title="Atendimentos", legend_title="Médico")
    fig.update_yaxes(showgrid=False)
    color_axes = '#000' if theme_toggle else '#90EE90'
    fig.update_xaxes(color=color_axes)
    fig.update_yaxes(color=color_axes)
    fig.update_layout(title_font_color=color_axes)
    fig.update_xaxes(showline=True, linecolor=color_axes)
    fig.update_yaxes(showline=True, linecolor=color_axes)
    return fig

# --- Atendimentos por ano ---
@callback(
    Output('atendimentos-mensais', 'figure'),
    [Input('dados-filtrados-store', 'data'),
     Input(ThemeSwitchAIO.ids.switch("theme"), 'value')]
)
def update_atendimentos_mensais(dados_filtrados_json, theme_toggle):
    import pandas as pd
    import plotly.graph_objects as go
    if not dados_filtrados_json:
        return go.Figure()
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return go.Figure()
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year.astype(int)
    df_group = df.groupby('ano', as_index=False).agg(atendimentos=('codigo_atendimento', pd.Series.nunique))
    anos = df_group['ano'].astype(str).tolist()
    valores = df_group['atendimentos'].tolist()
    textos = []
    text_colors = []
    for i, v in enumerate(valores):
        valor_str = f"{v:,}".replace(",", ".")
        if i == 0:
            textos.append(valor_str)
            text_colors.append('deeppink')
        else:
            prev = valores[i-1]
            if prev == 0:
                textos.append(valor_str)
                text_colors.append('deeppink')
            else:
                perc = (v - prev) / prev * 100
                sinal = '+' if perc > 0 else ''
                perc_str = f'({sinal}{perc:.1f}%)'
                cor = 'green' if perc > 0 else 'red'
                textos.append(f'{valor_str} {perc_str}')
                text_colors.append(cor)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=anos,
        y=valores,
        mode='lines+markers+text',
        text=textos,
        textposition='top center',
        textfont=dict(size=14, color=text_colors),
        line=dict(color='#007bff', width=3)
    ))
    y_max = max(valores) if valores else 1
    fig.update_layout(title="Atendimentos por Ano", xaxis_title="Ano", yaxis_title="Atendimentos", margin=dict(t=120))
    fig.update_yaxes(showgrid=False, range=[0, y_max * 1.10])
    color_axes = '#000' if theme_toggle else '#90EE90'
    fig.update_xaxes(color=color_axes)
    fig.update_yaxes(color=color_axes)
    fig.update_layout(title_font_color=color_axes)
    fig.update_xaxes(showline=True, linecolor=color_axes)
    fig.update_yaxes(showline=True, linecolor=color_axes)
    return fig

# --- Ticket Médio por Atendimento (R$) ---
@callback(
    Output('producao-medica-por-ano', 'figure'),
    [Input('dados-filtrados-store', 'data'),
     Input(ThemeSwitchAIO.ids.switch("theme"), 'value')]
)
def update_producao_medica_por_ano(dados_filtrados_json, theme_toggle):
    import pandas as pd
    import plotly.graph_objects as go
    if not dados_filtrados_json:
        return go.Figure()
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return go.Figure()
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year.astype(int)
    df_group = df.groupby('ano', as_index=False).agg(valor_total=('valor_total_unico', 'sum'), atendimentos=('codigo_atendimento', pd.Series.nunique))
    df_group['ticket_medio'] = df_group.apply(lambda row: row['valor_total'] / row['atendimentos'] if row['atendimentos'] > 0 else 0, axis=1)
    anos = df_group['ano'].astype(str).tolist()
    valores = df_group['ticket_medio'].tolist()
    textos = []
    text_colors = []
    for i, v in enumerate(valores):
        valor_str = f"R$ {v:,.2f}".replace(",", ".")
        if i == 0:
            textos.append(valor_str)
            text_colors.append('deeppink')
        else:
            prev = valores[i-1]
            if prev == 0:
                textos.append(valor_str)
                text_colors.append('deeppink')
            else:
                perc = (v - prev) / prev * 100
                sinal = '+' if perc > 0 else ''
                perc_str = f'({sinal}{perc:.1f}%)'
                cor = 'green' if perc > 0 else 'red'
                textos.append(f'{valor_str} {perc_str}')
                text_colors.append(cor)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=anos,
        y=valores,
        mode='lines+markers+text',
        text=textos,
        textposition='top center',
        textfont=dict(size=14, color=text_colors),
        line=dict(color='#007bff', width=3)
    ))
    y_max = max(valores) if valores else 1
    fig.update_layout(title="Ticket Médio por Atendimento (R$)", xaxis_title="Ano", yaxis_title="Ticket Médio (R$)", margin=dict(t=120))
    fig.update_yaxes(showgrid=False, range=[0, y_max * 1.10])
    color_axes = '#000' if theme_toggle else '#90EE90'
    fig.update_xaxes(color=color_axes)
    fig.update_yaxes(color=color_axes)
    fig.update_layout(title_font_color=color_axes)
    fig.update_xaxes(showline=True, linecolor=color_axes)
    fig.update_yaxes(showline=True, linecolor=color_axes)
    return fig

# --- Ticket Médio por Procedimento por Médico por Ano ---
@callback(
    Output('grid-ticket-medio-procedimento-por-medico-ano', 'children'),
    [Input('dados-filtrados-store', 'data')]
)
def update_grid_ticket_medio_procedimento_por_medico_ano(dados_filtrados_json):
    import pandas as pd
    from dash import dash_table
    if not dados_filtrados_json:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year
    df_group = df.groupby(['profissional', 'ano']).agg(valor_total=('valor_total_unico', 'sum'), procedimentos=('item', 'count')).reset_index()
    anos = sorted(df_group['ano'].unique())
    medicos = sorted(df_group['profissional'].unique())
    tabela = []
    for medico in medicos:
        linha = {'Médico': medico}
        total_valor = 0
        total_proc = 0
        for ano in anos:
            sub = df_group[(df_group['profissional'] == medico) & (df_group['ano'] == ano)]
            if not sub.empty and sub.iloc[0]['procedimentos'] > 0:
                ticket = sub.iloc[0]['valor_total'] / sub.iloc[0]['procedimentos']
                total_valor += sub.iloc[0]['valor_total']
                total_proc += sub.iloc[0]['procedimentos']
            else:
                ticket = 0
            linha[str(ano)] = ticket
        linha['Total Geral'] = total_valor / total_proc if total_proc > 0 else 0
        tabela.append(linha)
    total_geral_linha = {'Médico': 'Total Geral'}
    for ano in anos:
        total_valor_ano = df_group[df_group['ano'] == ano]['valor_total'].sum()
        total_proc_ano = df_group[df_group['ano'] == ano]['procedimentos'].sum()
        total_geral_linha[str(ano)] = total_valor_ano / total_proc_ano if total_proc_ano > 0 else 0
    total_valor_geral = df_group['valor_total'].sum()
    total_proc_geral = df_group['procedimentos'].sum()
    total_geral_linha['Total Geral'] = total_valor_geral / total_proc_geral if total_proc_geral > 0 else 0
    tabela.append(total_geral_linha)
    columns = [{'name': 'Ticket Médio / Procedimento (R$)', 'id': 'Médico'}]
    columns += [{'name': str(ano), 'id': str(ano)} for ano in anos]
    columns += [{'name': 'Total Geral', 'id': 'Total Geral'}]
    for linha in tabela:
        for ano in anos:
            linha[str(ano)] = f"R$ {linha[str(ano)]:,.2f}".replace(",", ".")
        linha['Total Geral'] = f"R$ {linha['Total Geral']:,.2f}".replace(",", ".")
    return dash_table.DataTable(
        columns=columns,
        data=tabela,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
        style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'}
    )

# --- Relação Procedimentos por Atendimento por Ano ---
@callback(
    Output('grafico-relacao-procedimentos-por-atendimento-ano', 'figure'),
    [Input('dados-filtrados-store', 'data'),
     Input(ThemeSwitchAIO.ids.switch("theme"), 'value')]
)
def update_grafico_relacao_procedimentos_por_atendimento_ano(dados_filtrados_json, theme_toggle):
    import pandas as pd
    import plotly.graph_objects as go
    if not dados_filtrados_json:
        return go.Figure()
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return go.Figure()
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year.astype(int)
    df_group = df.groupby('ano').agg(procedimentos=('item', 'count'), atendimentos=('codigo_atendimento', pd.Series.nunique)).reset_index()
    df_group = df_group.sort_values('ano')
    anos = df_group['ano'].astype(str).tolist()  # garantir anos únicos e ordenados
    relacao = df_group.apply(lambda row: row['procedimentos'] / row['atendimentos'] if row['atendimentos'] > 0 else 0, axis=1).tolist()
    textos = []
    text_colors = []
    for i, v in enumerate(relacao):
        valor_str = f"{v:.2f}"
        if i == 0:
            textos.append(valor_str)
            text_colors.append('deeppink')
        else:
            prev = relacao[i-1]
            if prev == 0:
                textos.append(valor_str)
                text_colors.append('deeppink')
            else:
                perc = (v - prev) / prev * 100
                sinal = '+' if perc > 0 else ''
                perc_str = f'({sinal}{perc:.1f}%)'
                cor = 'green' if perc > 0 else 'red'
                textos.append(f'{valor_str} {perc_str}')
                text_colors.append(cor)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=anos,
        y=relacao,
        mode='lines+markers+text',
        text=textos,
        textposition='top center',
        textfont=dict(size=14, color=text_colors),
        line=dict(color='#007bff', width=3),
        marker=dict(size=10, color='#007bff')
    ))
    y_max = max(relacao) if relacao else 1
    fig.update_layout(title="Relação Procedimentos por Atendimento por Ano", xaxis_title="Ano", yaxis_title="Qtde de Procedimentos / Atendimento", margin=dict(t=160))
    fig.update_yaxes(showgrid=False, range=[0, y_max * 1.15])
    color_axes = '#000' if theme_toggle else '#90EE90'
    fig.update_xaxes(color=color_axes)
    fig.update_yaxes(color=color_axes)
    fig.update_layout(title_font_color=color_axes)
    fig.update_xaxes(showline=True, linecolor=color_axes)
    fig.update_yaxes(showline=True, linecolor=color_axes)
    return fig

# ... existing code ...

@callback(
    Output('quantidade-total-por-medico-ano', 'children'),
    [Input('dados-filtrados-store', 'data')]
)
def update_quantidade_total_por_medico_ano(dados_filtrados_json):
    import pandas as pd
    from dash import dash_table
    if not dados_filtrados_json:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year.astype(int)
    df_group = df.groupby(['profissional', 'ano']).agg(quantidade_total=('codigo_atendimento', pd.Series.nunique)).reset_index()
    anos = sorted(df_group['ano'].unique())
    medicos = sorted(df_group['profissional'].unique())
    tabela = []
    for medico in medicos:
        linha = {'Médico': medico}
        total_geral = 0
        for ano in anos:
            valor = df_group[(df_group['profissional'] == medico) & (df_group['ano'] == ano)]['quantidade_total'].sum()
            linha[str(ano)] = valor
            total_geral += valor
        linha['Total Geral'] = total_geral
        tabela.append(linha)
    total_geral_linha = {'Médico': 'Total Geral'}
    for ano in anos:
        total_geral_linha[str(ano)] = sum(linha[str(ano)] for linha in tabela)
    total_geral_linha['Total Geral'] = sum(linha['Total Geral'] for linha in tabela)
    tabela.append(total_geral_linha)
    columns = [{'name': 'Quantidade Total de Atendimentos', 'id': 'Médico'}]
    columns += [{'name': str(ano), 'id': str(ano)} for ano in anos]
    columns += [{'name': 'Total Geral', 'id': 'Total Geral'}]
    for linha in tabela:
        for ano in anos:
            linha[str(ano)] = f"{linha[str(ano)]:,.0f}".replace(",", ".")
        linha['Total Geral'] = f"{linha['Total Geral']:,.0f}".replace(",", ".")
    return dash_table.DataTable(
        columns=columns,
        data=tabela,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
        style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'}
    )

@callback(
    Output('grid-ticket-medio-por-medico-ano', 'children'),
    [Input('dados-filtrados-store', 'data')]
)
def update_grid_ticket_medio_por_medico_ano(dados_filtrados_json):
    import pandas as pd
    from dash import dash_table
    if not dados_filtrados_json:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df = pd.read_json(io.StringIO(dados_filtrados_json), orient='split')
    if df.empty:
        return dash_table.DataTable(columns=[{"name": "", "id": "vazio"}], data=[])
    df['ano'] = pd.to_datetime(df['data_atendimento']).dt.year.astype(int)
    df_group = df.groupby(['profissional', 'ano']).agg(valor_total=('valor_total_unico', 'sum'), atendimentos=('codigo_atendimento', pd.Series.nunique)).reset_index()
    anos = sorted(df_group['ano'].unique())
    medicos = sorted(df_group['profissional'].unique())
    tabela = []
    for medico in medicos:
        linha = {'Médico': medico}
        total_valor = 0
        total_atend = 0
        for ano in anos:
            sub = df_group[(df_group['profissional'] == medico) & (df_group['ano'] == ano)]
            if not sub.empty and sub.iloc[0]['atendimentos'] > 0:
                ticket = sub.iloc[0]['valor_total'] / sub.iloc[0]['atendimentos']
                total_valor += sub.iloc[0]['valor_total']
                total_atend += sub.iloc[0]['atendimentos']
            else:
                ticket = 0
            linha[str(ano)] = ticket
        linha['Total Geral'] = total_valor / total_atend if total_atend > 0 else 0
        tabela.append(linha)
    total_geral_linha = {'Médico': 'Total Geral'}
    for ano in anos:
        total_valor_ano = df_group[df_group['ano'] == ano]['valor_total'].sum()
        total_atend_ano = df_group[df_group['ano'] == ano]['atendimentos'].sum()
        total_geral_linha[str(ano)] = total_valor_ano / total_atend_ano if total_atend_ano > 0 else 0
    total_valor_geral = df_group['valor_total'].sum()
    total_atend_geral = df_group['atendimentos'].sum()
    total_geral_linha['Total Geral'] = total_valor_geral / total_atend_geral if total_atend_geral > 0 else 0
    tabela.append(total_geral_linha)
    columns = [{'name': 'Ticket Médio / Atendimento (R$)', 'id': 'Médico'}]
    columns += [{'name': str(ano), 'id': str(ano)} for ano in anos]
    columns += [{'name': 'Total Geral', 'id': 'Total Geral'}]
    for linha in tabela:
        for ano in anos:
            linha[str(ano)] = f"R$ {linha[str(ano)]:,.2f}".replace(",", ".")
        linha['Total Geral'] = f"R$ {linha['Total Geral']:,.2f}".replace(",", ".")
    return dash_table.DataTable(
        columns=columns,
        data=tabela,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'fontWeight': 'bold'},
        style_header={'backgroundColor': '#888', 'color': 'white', 'fontWeight': 'bold'}
    )

@callback(
    Output("segmentos-container", "children", allow_duplicate=True),
    [Input("todos-segmentos-checkbox", "value")],
    prevent_initial_call='initial_duplicate'
)
def renderizar_segmentos(todos_value):
    from database.queries import get_segmentos
    segmentos = get_segmentos()
    checkboxes = []
    for segmento in segmentos:
        checkboxes.append(
            dbc.Checkbox(
                id={"type": "segmento-checkbox", "index": segmento["nome"]},
                label=segmento["nome"],
                value=True,
                className="d-block"
            )
        )
    return checkboxes

@callback(
    [Output({"type": "segmento-checkbox", "index": ALL}, "value"),
     Output("todos-segmentos-checkbox", "value")],
    [Input("todos-segmentos-checkbox", "value"),
     Input({"type": "segmento-checkbox", "index": ALL}, "value")],
    prevent_initial_call=False
)
def sync_segmentos_checkboxes(todos_value, segmento_values):
    from dash import ctx
    n = len(segmento_values)
    trigger_id = ctx.triggered_id

    def is_checked(val):
        if isinstance(val, list):
            return bool(val)
        return bool(val)

    todos_checked = is_checked(todos_value)

    # Se o trigger foi o botão TODOS
    if trigger_id == "todos-segmentos-checkbox":
        if todos_checked:
            return [True] * n, True
        else:
            return [False] * n, False

    # Se o trigger foi algum checkbox individual
    all_checked = all(is_checked(v) for v in segmento_values)
    return segmento_values, all_checked

# ... existing code ...
# --- CALLBACKS DE PROCEDIMENTOS (migrados de pages/atendimentos.py) ---
from dash import callback, Input, Output, State, ALL, html
import dash_bootstrap_components as dbc

PROCEDIMENTOS_PER_PAGE = 20

def get_procedimentos():
    from database.queries import get_procedimentos
    return get_procedimentos()

@callback(
    Output("procedimentos-page-store", "data"),
    [Input("procedimentos-anterior-btn", "n_clicks"),
     Input("procedimentos-proxima-btn", "n_clicks")],
    [State("procedimentos-page-store", "data")],
    prevent_initial_call=False
)
def navegar_paginas_procedimentos(n_anterior, n_proxima, page_data):
    page = page_data["page"] if page_data and "page" in page_data else 0
    total_procedimentos = len(get_procedimentos())
    n_pages = (total_procedimentos - 1) // PROCEDIMENTOS_PER_PAGE + 1
    from dash import callback_context
    changed_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    if changed_id == "procedimentos-anterior-btn" and page > 0:
        page -= 1
    elif changed_id == "procedimentos-proxima-btn" and page < n_pages-1:
        page += 1
    return {"page": page}

@callback(
    Output("procedimentos-container", "children"),
    [Input("procedimentos-page-store", "data"),
     Input("procedimentos-selecoes-store", "data")]
)
def renderizar_procedimentos(page_data, selecoes_store):
    procedimentos = get_procedimentos()
    total_procedimentos = len(procedimentos)
    page = page_data.get("page", 0) if page_data else 0
    start = page * PROCEDIMENTOS_PER_PAGE
    end = min(start + PROCEDIMENTOS_PER_PAGE, total_procedimentos)

    # Inicializa store se necessário
    if not selecoes_store or len(selecoes_store) != total_procedimentos:
        selecoes_store = {str(i): True for i in range(total_procedimentos)}
    checkboxes = []
    for idx in range(start, end):
        procedimento = procedimentos[idx]
        checkboxes.append(
            dbc.Checkbox(
                id={"type": "procedimento-checkbox", "index": idx},
                label=procedimento["nome"],
                value=selecoes_store.get(str(idx), True),
                className="d-block"
            )
        )
    n_pages = (total_procedimentos - 1) // PROCEDIMENTOS_PER_PAGE + 1
    nav_buttons = dbc.Row([
        dbc.Col(dbc.Button("Anterior", id="procedimentos-anterior-btn", n_clicks=0, disabled=page==0)),
        dbc.Col(html.Span(f"Página {page+1} de {n_pages}")),
        dbc.Col(dbc.Button("Próxima", id="procedimentos-proxima-btn", n_clicks=0, disabled=page==n_pages-1)),
    ], className="mt-2 mb-2 g-2", justify="center")
    return [*checkboxes, nav_buttons]



@callback(
    [Output({"type": "procedimento-checkbox", "index": ALL}, "value"),
     Output("todos-procedimentos-checkbox", "value"),
     Output("procedimentos-selecoes-store", "data", allow_duplicate=True)],
    [Input("todos-procedimentos-checkbox", "value"),
     Input({"type": "procedimento-checkbox", "index": ALL}, "value")],
    [State("procedimentos-selecoes-store", "data"), 
     State("procedimentos-page-store", "data")],
    prevent_initial_call=True
)
def sync_procedimentos_checkboxes(todos_value, procedimento_values, selecoes_store, page_data):
    from dash import ctx
    import dash

    # Obter lista completa de procedimentos
    procedimentos = get_procedimentos()
    total_procedimentos = len(procedimentos)

    # Inicializar store se necessário
    if not selecoes_store or len(selecoes_store) != total_procedimentos:
        selecoes_store = {str(i): True for i in range(total_procedimentos)}
    
    # Obter página atual
    page = page_data.get("page", 0) if page_data else 0
    start = page * PROCEDIMENTOS_PER_PAGE
    end = min(start + PROCEDIMENTOS_PER_PAGE, total_procedimentos)
    
    # Obter trigger
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Se o trigger foi o checkbox "TODOS"
    if trigger_id == "todos-procedimentos-checkbox":
        # Atualizar todos os itens no store com o valor do checkbox TODOS
        novo_estado = todos_value if todos_value is not None else False
        selecoes_store = {str(i): novo_estado for i in range(total_procedimentos)}
        
        # Retornar valores apenas para a página atual
        page_values = [novo_estado] * (end - start)
        
        return page_values, novo_estado, selecoes_store
    
    # Se o trigger foi um checkbox individual
    else:
        # Atualizar store com os valores da página atual
        if procedimento_values and len(procedimento_values) == (end - start):
            for idx, val in enumerate(procedimento_values):
                selecoes_store[str(start + idx)] = val
        
        # Verificar se todos estão marcados
        todos_marcados = all(selecoes_store.values())
        
        # Obter valores atualizados para a página atual
        page_values = [selecoes_store.get(str(i), False) for i in range(start, end)]
        
        return page_values, todos_marcados, selecoes_store


@callback(
    Output("segmentos-container", "children"),
    [Input("todos-segmentos-checkbox", "value")],
    prevent_initial_call=False
)
def renderizar_segmentos(todos_value):
    from database.queries import get_segmentos
    segmentos = get_segmentos()
    checkboxes = []
    for segmento in segmentos:
        checkboxes.append(
            dbc.Checkbox(
                id={"type": "segmento-checkbox", "index": segmento["nome"]},
                label=segmento["nome"],
                value=True,
                className="d-block"
            )
        )
    return checkboxes

@callback(
    Output("tipos-atendimento-container", "children"),
    [Input("todos-segmentos-checkbox", "value")],
    prevent_initial_call=False
)
def renderizar_tipos_atendimento(todos_value):
    tipos_atendimento = get_tipos_atendimento()
    tipos_atendimento_checkboxes = [
        dbc.Checkbox(
            id={"type": "segmento-checkbox", "index": item['nome']},
            label=item['nome'],
            value=True if todos_value else False,
            className="d-block"
        ) for item in tipos_atendimento
    ]
    return html.Div(tipos_atendimento_checkboxes, id="tipos-atendimento-checkboxes-container")

