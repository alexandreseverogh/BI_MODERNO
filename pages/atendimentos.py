from dash import html, dcc
import dash_bootstrap_components as dbc
from data.database import execute_query
from database.queries import get_years, get_min_max_data_atendimento
import calendar

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

def layout():
    azul = "#0d47a1"
    azul_valor = "#2196f3"
    meses_abrev = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
    card_dark = {"background": "#23272f", "border": "none", "boxShadow": "0 2px 8px #0003"}
    text_white = {"color": "#fff"}
    checkbox_style = {"color": "#fff", "background": "#23272f", "border": "none"}
    datepicker_style = {"background": "#23272f", "color": "#fff", "border": "1px solid #444"}
    return dbc.Container([
        # Linha de título principal
        dbc.Row([
            dbc.Col([
                html.H2("Produção Médica", className="text-center fw-bold mb-4", style={"fontSize": "2.2rem", "color": azul})
            ], width=12)
        ]),
        # Container estilizado para filtros superiores (DARK)
        dbc.Card([
            dbc.CardBody([
                # Primeira linha: apenas ANOS
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Span("ANOS:", style={"fontWeight": "bold", "marginRight": "8px", "color": "#fff"}),
                            dbc.Checkbox(id="todos-anos-checkbox", label="TODOS", value=True, className="d-inline-block me-2", style={"marginRight": "12px", "verticalAlign": "middle", **checkbox_style}),
                            *[
                                dbc.Checkbox(
                                    id={"type": "year-checkbox", "index": year},
                                    label=str(year),
                                    value=True,
                                    className="d-inline-block me-2",
                                    style={"verticalAlign": "middle", **checkbox_style}
                                ) for year in years
                            ],
                        ], className="d-flex align-items-center flex-wrap"),
                    ], width=12),
                ], align="center", className="mb-1"),
                # Segunda linha: MESES e datas
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Span("MESES:", style={"fontWeight": "bold", "marginRight": "8px", "color": "#fff"}),
                            dbc.Checkbox(id="todos-meses-checkbox", label="TODOS", value=True, className="d-inline-block me-2", style={"marginRight": "12px", "verticalAlign": "middle", **checkbox_style}),
                            *[
                                dbc.Checkbox(
                                    id={"type": "month-checkbox", "index": month},
                                    label=meses_abrev[month-1],
                                    value=True,
                                    className="d-inline-block me-2",
                                    style={"verticalAlign": "middle", **checkbox_style}
                                ) for month in months
                            ],
                            # Barra vertical
                            html.Span("|", style={"margin": "0 16px", "fontWeight": "bold", "fontSize": "18px", "color": "#fff"}),
                            # DATA INICIAL e DATA FINAL
                            html.Span("DATA INICIAL", style={"fontWeight": "bold", "marginRight": "5px", "color": "#fff"}),
                            dcc.DatePickerSingle(
                                id="data_inicial",
                                display_format="DD/MM/YYYY",
                                style={**datepicker_style, "marginRight": "10px"},
                                min_date_allowed=min_data,
                                max_date_allowed=max_data,
                                date=min_data
                            ),
                            html.Span("DATA FINAL", style={"fontWeight": "bold", "marginRight": "5px", "color": "#fff"}),
                            dcc.DatePickerSingle(
                                id="data_final",
                                display_format="DD/MM/YYYY",
                                style=datepicker_style,
                                min_date_allowed=min_data,
                                max_date_allowed=max_data,
                                date=max_data
                            ),
                        ], className="d-flex align-items-center flex-wrap"),
                    ], width=12),
                ], align="center", className="mb-0"),
            ])
        ], className="mb-3 shadow-sm p-2", style=card_dark),

        # Container estilizado para os filtros principais (DARK)
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    # Filtro 1
                    html.Div([
                        html.H4("CONVENIOS", className="mb-1 text-start fw-bold", style={"color": azul}),
                        dbc.Checkbox(id="todos-pagamentos-checkbox", label="TODOS", value=True, className="d-block mb-2", style=checkbox_style),
                        dbc.Button("Opções", id="collapse-pagamentos-btn", color="secondary", size="sm", className="mb-2", n_clicks=0, style={"background": "#23272f", "color": "#fff", "border": "1px solid #444"}),
                        dbc.Collapse(
                            html.Div(id="pagamentos-container", style={"maxHeight": "200px", "overflowY": "auto"}),
                            id="collapse-pagamentos", is_open=False
                        )
                    ], style={"flex": "1", "minWidth": "0"}),
                    # Linha vertical
                    html.Div(style={"borderLeft": "2px solid #444", "height": "100px", "margin": "0 8px"}),
                    # Filtro 2
                    html.Div([
                        html.H4("MEDICOS", className="mb-1 text-start fw-bold", style={"color": azul}),
                        dbc.Checkbox(id="todos-profissionais-checkbox", label="TODOS", value=True, className="d-block mb-2", style=checkbox_style),
                        dbc.Button("Opções", id="collapse-profissionais-btn", color="secondary", size="sm", className="mb-2", n_clicks=0, style={"background": "#23272f", "color": "#fff", "border": "1px solid #444"}),
                        dbc.Collapse(
                            html.Div(id="profissionais-container", style={"maxHeight": "200px", "overflowY": "auto"}),
                            id="collapse-profissionais", is_open=False
                        )
                    ], style={"flex": "1", "minWidth": "0"}),
                    # Linha vertical
                    html.Div(style={"borderLeft": "2px solid #444", "height": "100px", "margin": "0 8px"}),
                    # Filtro 3
                    html.Div([
                        html.H4("PROCEDIMENTOS", className="mb-1 text-start fw-bold", style={"color": azul}),
                        dbc.Checkbox(id="todos-especialidades-checkbox", label="TODOS", value=True, className="d-block mb-2", style=checkbox_style),
                        dbc.Button("Opções", id="collapse-especialidades-btn", color="secondary", size="sm", className="mb-2", n_clicks=0, style={"background": "#23272f", "color": "#fff", "border": "1px solid #444"}),
                        dbc.Collapse(
                            html.Div(id="especialidades-container", style={"maxHeight": "200px", "overflowY": "auto"}),
                            id="collapse-especialidades", is_open=False
                        )
                    ], style={"flex": "1", "minWidth": "0"}),
                    # Linha vertical
                    html.Div(style={"borderLeft": "2px solid #444", "height": "100px", "margin": "0 8px"}),
                    # Filtro 4
                    html.Div([
                        html.H4("SEGMENTOS", className="mb-1 text-start fw-bold", style={"color": azul}),
                        dbc.Checkbox(id="todos-segmentos-checkbox", label="TODOS", value=True, className="d-block mb-2", style=checkbox_style),
                        dbc.Button("Opções", id="collapse-segmentos-btn", color="secondary", size="sm", className="mb-2", n_clicks=0, style={"background": "#23272f", "color": "#fff", "border": "1px solid #444"}),
                        dbc.Collapse(
                            html.Div(id="segmentos-container", style={"maxHeight": "200px", "overflowY": "auto"}),
                            id="collapse-segmentos", is_open=False
                        )
                    ], style={"flex": "1", "minWidth": "0"}),
                ], style={"display": "flex", "alignItems": "stretch", "justifyContent": "space-between"})
            ])
        ], className="mb-4 shadow-sm p-2", style=card_dark),

        # Gráficos (cards e gráficos principais)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total de Atendimentos", className="card-title text-center fw-bold", style={"fontSize": "1.5rem", **text_white}),
                        html.H2(id="total-atendimentos", className="card-text text-center", style={"color": azul_valor})
                    ])
                ], style=card_dark)
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Valor Total", className="card-title text-center fw-bold", style={"fontSize": "1.5rem", **text_white}),
                        html.H2(id="valor-total", className="card-text text-center", style={"color": azul_valor})
                    ])
                ], style=card_dark)
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Ticket Médio", className="card-title text-center fw-bold", style={"fontSize": "1.5rem", **text_white}),
                        html.H2(id="ticket-medio", className="card-text text-center", style={"color": azul_valor})
                    ])
                ], style=card_dark)
            ], md=4)
        ], className="mb-4"),

        # Gráfico de atendimentos por mês (linha separada)
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="atendimentos-mensais", config={"displayModeBar": False}),
                html.H4("Atendimentos Mensais", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem", **text_white})
            ], md=12)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id="top-profissionais"),
                html.H4("Top Profissionais", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
            ], md=4),
            dbc.Col([
                dcc.Graph(id="grafico-extra-1"),
                html.H4("Gráfico Extra 1", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
            ], md=4),
            dbc.Col([
                dcc.Graph(id="grafico-extra-2"),
                html.H4("Gráfico Extra 2", className="text-center fw-bold mt-2", style={"fontSize": "1.3rem"})
            ], md=4),
        ])
    ], fluid=True) 