import pandas as pd
from dash import html, dcc, callback, dash_table
from dash.dependencies import Input, Output, ALL, State
import dash_bootstrap_components as dbc
from data.database import execute_query
from database.queries import get_years, get_min_max_data_atendimento, get_dados_filtrados, get_segmentos, get_formas_pagamento, get_profissionais, get_procedimentos, get_total_segmentos_distinct, get_total_procedimentos_distinct
import calendar
from dash_bootstrap_templates import ThemeSwitchAIO, load_figure_template
import plotly.graph_objects as go
import datetime
import io
from dash import dcc, callback_context
#import dash_core_components as dcc  # ou from dash import dcc, se for Dash 2.x

# Adiciona estilo customizado para os checkboxes
checkbox_style = {
    "input": {
        "backgroundColor": "#90EE90",  # Verde claro para tema dark
        "borderColor": "#90EE90"
    }
}

def get_available_years():
    return sorted(get_years(), reverse=True)

years = get_available_years()
months = list(range(1, 13))

# Buscar datas reais do banco
min_data, max_data = get_min_max_data_atendimento()
if min_data:
    min_data = min_data.strftime('%Y-%m-%d')
else:
    min_data = '2020-01-01'
if max_data:
    max_data = max_data.strftime('%Y-%m-%d')
else:
    max_data = '2030-12-31'

# Load the figure templates for both themes
load_figure_template(["flatly", "darkly"])

url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

def get_graph_theme_settings(toggle):
    """Helper function to create consistent graph theme settings"""
    if toggle:  # Light theme
        return {
            "template": "flatly",
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
            "font": {"color": "black"},
            "xaxis": {
                "gridcolor": "rgba(0,0,0,0.1)",
                "zerolinecolor": "rgba(0,0,0,0.2)",
                "color": "black"
            },
            "yaxis": {
                "gridcolor": "rgba(0,0,0,0.1)",
                "zerolinecolor": "rgba(0,0,0,0.2)",
                "color": "black"
            },
            "margin": {"t": 50, "l": 50, "r": 20, "b": 50}
        }
    else:  # Dark theme
        return {
            "template": "darkly",
            "paper_bgcolor": "#2B3035",
            "plot_bgcolor": "#2B3035",
            "font": {"color": "white"},
            "xaxis": {
                "gridcolor": "rgba(255,255,255,0.1)",
                "zerolinecolor": "rgba(255,255,255,0.2)",
                "color": "white",
                "showgrid": True
            },
            "yaxis": {
                "gridcolor": "rgba(255,255,255,0.1)",
                "zerolinecolor": "rgba(255,255,255,0.2)",
                "color": "white",
                "showgrid": True
            },
            "margin": {"t": 50, "l": 50, "r": 20, "b": 50}
        }

def get_selected_filters(ctx, year_values, month_values, pagamento_values, profissional_values, segmento_values, procedimento_values, todos_anos, todos_meses, todos_pagamentos, todos_profissionais, todos_segmentos, todos_procedimentos):
    # ANOS: lógica simplificada
    if todos_anos:
        selected_years = [str(year) for year in get_years()]
    else:
        selected_years = [year_id for year_id, checked in zip([str(year) for year in get_years()], year_values) if checked]

    # MESES: lógica simplificada
    if todos_meses:
        selected_months = [str(month) for month in range(1, 13)]
    else:
        selected_months = [month_id for month_id, checked in zip([str(month) for month in range(1, 13)], month_values) if checked]

    # PAGAMENTOS: lógica simplificada
    if todos_pagamentos:
        selected_pagamentos = [pagamento["nome"] for pagamento in get_formas_pagamento()]
    else:
        selected_pagamentos = [pag_id for pag_id, checked in zip([pag["nome"] for pag in get_formas_pagamento()], pagamento_values) if checked]

    # PROFISSIONAIS: lógica simplificada
    if todos_profissionais:
        selected_profissionais = [profissional["nome"] for profissional in get_profissionais()]
    else:
        selected_profissionais = [prof_id for prof_id, checked in zip([prof["nome"] for prof in get_profissionais()], profissional_values) if checked]

    # SEGMENTOS: lógica simplificada
    if todos_segmentos:
        selected_segmentos = [segmento["nome"] for segmento in get_segmentos()]
    else:
        selected_segmentos = [segm_id for segm_id, checked in zip([segm["nome"] for segm in get_segmentos()], segmento_values) if checked]

    # PROCEDIMENTOS: lógica simplificada
    if todos_procedimentos:
        selected_procedimentos = [procedimento["nome"] for procedimento in get_procedimentos()]
    else:
        selected_procedimentos = [proc_id for proc_id, checked in zip([proc["nome"] for proc in get_procedimentos()], procedimento_values) if checked]

    return selected_years, selected_months, selected_pagamentos, selected_profissionais, selected_segmentos, selected_procedimentos

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

# Calcular tamanhos das listas de opções dos filtros apenas uma vez (estático)
N_PAGAMENTOS = len(get_formas_pagamento())
N_PROFISSIONAIS = len(get_profissionais())
N_SEGMENTOS = get_total_segmentos_distinct()
N_PROCEDIMENTOS = get_total_procedimentos_distinct()

def layout():
    meses_abrev = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
    total_procedimentos = len(get_procedimentos())
    return html.Div(id="main-container", className="theme-light", children=[
        dcc.Store(id='dados-filtrados-store'),
        dcc.Store(id="procedimentos-selecoes-store", data={str(i): True for i in range(total_procedimentos)}),
        dcc.Store(id="procedimentos-page-store", data={"page": 0}),
        dbc.Container([
            # Linha de título principal com Theme Switch
            dbc.Row([
                dbc.Col(width=4),  # Empty column for spacing
                dbc.Col([
                    html.H2("Produção Médica", id="producao-medica-title", className="fw-bold mb-0 text-center")
                ], width=4),
                dbc.Col([
                    html.Div([
                        ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2])
                    ], className="d-flex justify-content-end")
                ], width=4)
            ], className="mb-3"),

            # Container estilizado para filtros superiores
            dbc.Card([
                dbc.CardBody([
                    # Primeira linha: apenas ANOS
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Span("ANOS:", style={"fontWeight": "bold", "marginRight": "8px"}),
                                dbc.Checkbox(
                                    id="todos-anos-checkbox",
                                    label="TODOS",
                                    value=True,
                                    className="d-inline-block me-2 custom-checkbox theme-light",
                                    style={"marginRight": "12px", "verticalAlign": "middle"}
                                ),
                                *[
                                    dbc.Checkbox(
                                        id={"type": "year-checkbox", "index": year},
                                        label=str(year),
                                        value=True,
                                        className="d-inline-block me-2 custom-checkbox theme-light",
                                        style={"verticalAlign": "middle"}
                                    ) for year in years
                                ],
                            ], className="d-flex align-items-center flex-wrap"),
                        ], width=12),
                    ], align="center", className="mb-1"),
                    # Segunda linha: MESES e datas
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Span("MESES:", style={"fontWeight": "bold", "marginRight": "8px"}),
                                dbc.Checkbox(
                                    id="todos-meses-checkbox",
                                    label="TODOS",
                                    value=True,
                                    className="d-inline-block me-2 custom-checkbox theme-light",
                                    style={"marginRight": "12px", "verticalAlign": "middle"}
                                ),
                                *[
                                    dbc.Checkbox(
                                        id={"type": "month-checkbox", "index": month},
                                        label=meses_abrev[month-1],
                                        value=True,
                                        className="d-inline-block me-2 custom-checkbox theme-light",
                                        style={"verticalAlign": "middle"}
                                    ) for month in months
                                ],
                                # Barra vertical
                                html.Span("|", style={"margin": "0 16px", "fontWeight": "bold", "fontSize": "18px"}),
                                # DATA INICIAL e DATA FINAL
                                html.Div([
                                    html.Span("DATA INICIAL", style={"fontWeight": "bold", "marginRight": "5px"}),
                                    dcc.DatePickerSingle(
                                        id="data_inicial",
                                        display_format="DD/MM/YYYY",
                                        style={"marginRight": "10px"},
                                        min_date_allowed=min_data,
                                        max_date_allowed=max_data,
                                        date=min_data,
                                    ),
                                    html.Span("DATA FINAL", style={"fontWeight": "bold", "marginRight": "5px"}),
                                    dcc.DatePickerSingle(
                                        id="data_final",
                                        display_format="DD/MM/YYYY",
                                        min_date_allowed=min_data,
                                        max_date_allowed=max_data,
                                        date=max_data,
                                    ),
                                ], className="d-flex align-items-center"),
                            ], className="d-flex align-items-center flex-wrap"),
                        ], width=12),
                    ], align="center", className="mb-0"),
                ])
            ], className="mb-3 shadow-sm p-2"),

            # Container estilizado para os filtros principais
            html.Div(id="metrics-container", children=[
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            # Filtro 1
                            html.Div([
                                html.H4("CONVENIOS", id="convenios-title", className="mb-1 text-start fw-bold"),
                                dbc.Checkbox(
                                    id="todos-pagamentos-checkbox",
                                    label="TODOS",
                                    value=True,
                                    className="d-block mb-2 custom-checkbox"
                                ),
                                dbc.Button("Opções", 
                                         id="collapse-pagamentos-btn", 
                                         color="secondary", 
                                         size="sm", 
                                         className="mb-2",
                                         n_clicks=0),
                                dbc.Collapse(
                                    html.Div(id="pagamentos-container", style={"maxHeight": "200px", "overflowY": "auto"}),
                                    id="collapse-pagamentos", is_open=False
                                )
                            ], style={"flex": "1", "minWidth": "0"}),
                            # Linha vertical
                            html.Div(style={"borderLeft": "2px solid #dee2e6", "height": "100px", "margin": "0 8px"}),
                            # Filtro 2
                            html.Div([
                                html.H4("MÉDICOS", id="medicos-title", className="mb-1 text-start fw-bold"),
                                dbc.Checkbox(
                                    id="todos-profissionais-checkbox",
                                    label="TODOS",
                                    value=True,
                                    className="d-block mb-2 custom-checkbox"
                                ),
                                dbc.Button("Opções", 
                                         id="collapse-profissionais-btn", 
                                         color="secondary", 
                                         size="sm", 
                                         className="mb-2",
                                         n_clicks=0),
                                dbc.Collapse(
                                    html.Div(id="profissionais-container", style={"maxHeight": "200px", "overflowY": "auto"}),
                                    id="collapse-profissionais", is_open=False
                                )
                            ], style={"flex": "1", "minWidth": "0"}),
                            # Linha vertical
                            html.Div(style={"borderLeft": "2px solid #dee2e6", "height": "100px", "margin": "0 8px"}),
                            # Filtro 3
                            html.Div([
                                html.H4("PROCEDIMENTOS", id="procedimentos-title", className="mb-1 text-start fw-bold"),
                                dbc.Checkbox(
                                    id="todos-procedimentos-checkbox",
                                    label="TODOS",
                                    value=True,
                                    className="d-block mb-2 custom-checkbox"
                                ),
                                dbc.Button("Opções", 
                                         id="collapse-procedimentos-btn", 
                                         color="secondary", 
                                         size="sm", 
                                         className="mb-2",
                                         n_clicks=0),
                                dbc.Collapse(
                                    html.Div([
                                        dbc.Button("Anterior", id="procedimentos-anterior-btn", color="secondary", size="sm", className="me-2"),
                                        dbc.Button("Próxima", id="procedimentos-proxima-btn", color="secondary", size="sm"),
                                        html.Div(id="procedimentos-container", style={"maxHeight": "200px", "overflowY": "auto"})
                                    ]),
                                    id="collapse-procedimentos", is_open=False
                                )
                            ], style={"flex": "1", "minWidth": "0"}),
                            # Linha vertical
                            html.Div(style={"borderLeft": "2px solid #dee2e6", "height": "100px", "margin": "0 8px"}),
                            # Filtro 4
                            html.Div([
                                html.H4("SEGMENTOS", id="segmentos-title", className="mb-1 text-start fw-bold"),
                                dbc.Checkbox(
                                    id="todos-segmentos-checkbox",
                                    label="TODOS",
                                    value=True,
                                    className="d-block mb-2 custom-checkbox"
                                ),
                                dbc.Button("Opções", 
                                         id="collapse-segmentos-btn", 
                                         color="secondary", 
                                         size="sm", 
                                         className="mb-2",
                                         n_clicks=0),
                                dbc.Collapse(
                                    html.Div(id="segmentos-container", style={"maxHeight": "200px", "overflowY": "auto"}),
                                    id="collapse-segmentos", is_open=False
                                )
                            ], style={"flex": "1", "minWidth": "0"}),
                        ], style={"display": "flex", "alignItems": "stretch", "justifyContent": "space-between"})
                    ])
                ], className="mb-4 shadow-sm p-2"),
            ]),

            # Gráficos (cards e gráficos principais)
            html.Div(id="graphs-container", children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Total de Atendimentos", className="card-title text-center fw-bold", style={"fontSize": "1.5rem"}),
                                html.H2(id="total-atendimentos", className="card-text text-center")
                            ])
                        ])
                    ], md=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Total de Procedimentos", className="card-title text-center fw-bold", style={"fontSize": "1.5rem"}),
                                html.H2(id="total-procedimentos", className="card-text text-center")
                            ])
                        ])
                    ], md=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Valor Total", className="card-title text-center fw-bold", style={"fontSize": "1.5rem"}),
                                html.H2(id="valor-total", className="card-text text-center")
                            ])
                        ])
                    ], md=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Ticket Médio", className="card-title text-center fw-bold", style={"fontSize": "1.5rem"}),
                                html.H2(id="ticket-medio", className="card-text text-center")
                            ])
                        ])
                    ], md=3)
                ], className="mb-4"),

                # Gráfico de produção bruta mensal (MOVIDO PARA LOGO APÓS OS CARDS)
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="producao-bruta-mensal"),
                        html.H4("Valor da Produção Bruta (R$) / Média dos meses selecionados", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRÁFICO: Produção Bruta por Ano
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="producao-bruta-por-ano"),
                        html.H4("Produção Bruta por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRÁFICO: Produção Bruta por Médico por Ano
                dbc.Row([
                    dbc.Col([
                        html.Div(id="grid-producao-bruta-por-medico-ano"),
                        html.H4("Valor da Produção Bruta (R$) por Médico e Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRÁFICO: Atendimentos por Médico por Mês
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="atendimentos-por-medico-mensal"),
                        html.H4("Atendimentos por Médico por Mês", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # Gráfico de atendimentos por mês
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="atendimentos-mensais"),
                        html.H4("Atendimentos por ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRID: Quantidade Total por Médico por Ano
                dbc.Row([
                    dbc.Col([
                        html.Div(id="quantidade-total-por-medico-ano"),
                        html.H4("Quantidade Total de Atendimentos por Médico por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRÁFICO: Total de Procedimentos por Ano
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="total-procedimentos-por-ano"),
                        html.H4("Total de Procedimentos por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRID: Quantidade de Procedimentos por Médico por Ano
                dbc.Row([
                    dbc.Col([
                        html.Div(id="grid-procedimentos-por-medico-ano"),
                        html.H4("Quantidade de Procedimentos por Médico por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # Gráfico: Ticket Médio por Atendimento (R$)
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="producao-medica-por-ano"),
                        html.H4("Ticket Médio por Atendimento (R$)", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRID: Ticket Médio por Médico por Ano
                dbc.Row([
                    dbc.Col([
                        html.Div(id="grid-ticket-medio-por-medico-ano"),
                        html.H4("Ticket Médio por Médico por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # Gráfico: Ticket Médio por Procedimento por Ano (agora o último)
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="ticket-medio-por-procedimento-ano"),
                        html.H4("Ticket Médio por Procedimento por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRID: Ticket Médio por Procedimento por Médico por Ano
                dbc.Row([
                    dbc.Col([
                        html.Div(id="grid-ticket-medio-procedimento-por-medico-ano"),
                        html.H4("Ticket Médio por Procedimento por Médico por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRÁFICO: Relação Procedimentos por Atendimento por Ano
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="grafico-relacao-procedimentos-por-atendimento-ano"),
                        html.H4("Relação Procedimentos por Atendimento por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRID: Qtde de Procedimentos / Atendimento por Médico por Ano
                dbc.Row([
                    dbc.Col([
                        html.Div(id="grid-relacao-procedimentos-por-atendimento-por-medico-ano"),
                        html.H4("Qtde de Procedimentos / Atendimento por Médico por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),

                # NOVO GRÁFICO: Ticket Médio vs Quantidade de Atendimentos por Ano
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="grafico-ticket-medio-vs-quantidade-atendimentos-ano"),
                        html.H4("Ticket Médio vs Quantidade de Atendimentos por Ano", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
                    ], md=12)
                ], className="mb-4"),
            ])
        ], fluid=True)
    ])

# Theme callback for main container
@callback(
    Output("main-container", "className"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    prevent_initial_call=True
)
def update_theme(toggle):
    theme_class = "theme-light" if toggle else "theme-dark"
    return theme_class

@callback(
    Output('dados-filtrados-store', 'data'),
    [
        Input({"type": "year-checkbox", "index": ALL}, "value"),
        Input({"type": "month-checkbox", "index": ALL}, "value"),
        Input({"type": "pagamento-checkbox", "index": ALL}, "value"),
        Input({"type": "profissional-checkbox", "index": ALL}, "value"),
        Input({"type": "segmento-checkbox", "index": ALL}, "value"),
        Input({"type": "procedimento-checkbox", "index": ALL}, "value"),
        Input("todos-anos-checkbox", "value"),
        Input("todos-meses-checkbox", "value"),
        Input("todos-pagamentos-checkbox", "value"),
        Input("todos-profissionais-checkbox", "value"),
        Input("todos-procedimentos-checkbox", "value"),
        Input("data_inicial", "date"),
        Input("data_final", "date"),
        Input("todos-segmentos-checkbox", "value")
    ],
    prevent_initial_call=False
)
def update_dados_filtrados_store(
    year_values, month_values, pagamento_values,
    profissional_values, segmento_values, procedimento_values,
    todos_anos, todos_meses, todos_pagamentos,
    todos_profissionais, todos_procedimentos,
    data_inicial, data_final,
    todos_segmentos
):
    from dash import ctx
    try:
        years = get_years()
        months = list(range(1, 13))
        pagamentos = get_formas_pagamento()
        profissionais = get_profissionais()
        segmentos = get_segmentos()
        procedimentos = get_procedimentos()
        
        # Se nenhum valor selecionado, retorna DataFrame vazio
        if not year_values or len(year_values) != len(years) or all(v is None for v in year_values):
            year_values = [True] * len(years)
        if not month_values or len(month_values) != len(months) or all(v is None for v in month_values):
            month_values = [True] * len(months)
        if not pagamento_values or len(pagamento_values) != len(pagamentos) or all(v is None for v in pagamento_values):
            pagamento_values = [True] * len(pagamentos)
        if not profissional_values or len(profissional_values) != len(profissionais) or all(v is None for v in profissional_values):
            profissional_values = [True] * len(profissionais)
        if not segmento_values or len(segmento_values) != len(segmentos) or all(v is None for v in segmento_values):
            segmento_values = [True] * len(segmentos)
        if not procedimento_values or len(procedimento_values) != len(procedimentos) or all(v is None for v in procedimento_values):
            procedimento_values = [True] * len(procedimentos)

        print("[DEBUG] year_values:", year_values)
        print("[DEBUG] month_values:", month_values)
        print("[DEBUG] pagamento_values:", pagamento_values)
        print("[DEBUG] profissional_values:", profissional_values)
        print("[DEBUG] segmento_values:", segmento_values)
        print("[DEBUG] procedimento_values:", procedimento_values)

        selected_years, selected_months, selected_pagamentos, selected_profissionais, selected_segmentos, selected_procedimentos = get_selected_filters(
            ctx, year_values, month_values, pagamento_values, profissional_values, segmento_values, procedimento_values,
            todos_anos, todos_meses, todos_pagamentos,
            todos_profissionais, todos_segmentos, todos_procedimentos
        )

        print("[DEBUG][callback] selected_years:", selected_years, "(len:", len(selected_years), ")")
        print("[DEBUG][callback] selected_months:", selected_months, "(len:", len(selected_months), ")")
        print("[DEBUG][callback] selected_pagamentos:", selected_pagamentos, "(len:", len(selected_pagamentos), ")")
        print("[DEBUG][callback] selected_profissionais:", selected_profissionais, "(len:", len(selected_profissionais), ")")
        print("[DEBUG][callback] selected_segmentos:", selected_segmentos, "(len:", len(selected_segmentos), ")")
        print("[DEBUG][callback] selected_procedimentos:", selected_procedimentos, "(len:", len(selected_procedimentos), ")")

        # NOVA LÓGICA: se qualquer filtro principal vier vazio, retorna DataFrame vazio
        if (not selected_years or not selected_months or not selected_pagamentos or not selected_profissionais or not selected_segmentos or not selected_procedimentos):
            print("[DEBUG] Algum filtro principal está vazio. Retornando DataFrame vazio.")
            return pd.DataFrame().to_json(date_format='iso', orient='split')

        data_inicial_iso = converter_para_iso(data_inicial)
        data_final_iso = converter_para_iso(data_final)
        print("[DEBUG] data_inicial_iso:", data_inicial_iso)
        print("[DEBUG] data_final_iso:", data_final_iso)

        df = get_dados_filtrados(
            anos=selected_years,
            meses=selected_months,
            formas_pagamento=selected_pagamentos,
            profissionais=selected_profissionais,
            segmentos=selected_segmentos,
            procedimentos=selected_procedimentos,
            data_inicial=data_inicial_iso,
            data_final=data_final_iso
        )

        print("[DEBUG] df shape:", df.shape if df is not None else None)
        if df is not None:
            print("[DEBUG] df head:\n", df.head())
        if df is not None and not df.empty:
            df['ano'] = df['ano_atendimento']
            df['mes'] = df['mes_atendimento']
            return df.to_json(date_format='iso', orient='split')
        else:
            print("[DEBUG] DataFrame está vazio após filtro.")
            return pd.DataFrame().to_json(date_format='iso', orient='split')
    except Exception as e:
        print("[ERRO] Callback update_dados_filtrados_store falhou:", e)
        import traceback; traceback.print_exc()
        return pd.DataFrame().to_json(date_format='iso', orient='split')


def get_procedimentos():
    from database.queries import get_procedimentos
    return get_procedimentos()

