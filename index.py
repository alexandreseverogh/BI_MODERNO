from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from app import app, server
from pages import atendimentos
import callbacks.atendimentos  # Updated import for callbacks

# Layout da página inicial
def create_home_layout():
    return dbc.Container([
        html.H1("GORE", className="text-center mt-4 mb-4"),
        
        # Primeira linha de ícones
        dbc.Row([
            # Atendimentos
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.I(className="fas fa-user-clock fa-2x text-info"),
                        html.H5("Atendimentos", className="mt-3"),
                        dbc.CardLink("", href="/atendimentos", className="stretched-link")
                    ], className="text-center"),
                    className="menu-card h-100"
                )
            ], width={"size": 3, "offset": 0}),
            
            # Agendamentos
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.I(className="fas fa-calendar-alt fa-2x text-success"),
                        html.H5("Agendamentos", className="mt-3"),
                        dbc.CardLink("", href="/agendamentos", className="stretched-link")
                    ], className="text-center"),
                    className="menu-card h-100"
                )
            ], width=3),
            
            # Convênios
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.I(className="fas fa-handshake fa-2x text-primary"),
                        html.H5("Convênios", className="mt-3"),
                        dbc.CardLink("", href="/convenios", className="stretched-link")
                    ], className="text-center"),
                    className="menu-card h-100"
                )
            ], width=3),
            
            # Clientes
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.I(className="fas fa-users fa-2x text-warning"),
                        html.H5("Clientes", className="mt-3"),
                        dbc.CardLink("", href="/clientes", className="stretched-link")
                    ], className="text-center"),
                    className="menu-card h-100"
                )
            ], width=3),
        ], className="mb-4"),
        
        # Segunda linha de ícones
        dbc.Row([
            # Contas a Pagar
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.I(className="fas fa-money-bill-wave fa-2x text-danger"),
                        html.H5("Contas a Pagar", className="mt-3"),
                        dbc.CardLink("", href="/contas-pagar", className="stretched-link")
                    ], className="text-center"),
                    className="menu-card h-100"
                )
            ], width=3),
            
            # Contas a Receber
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.I(className="fas fa-hand-holding-usd fa-2x text-success"),
                        html.H5("Contas a Receber", className="mt-3"),
                        dbc.CardLink("", href="/contas-receber", className="stretched-link")
                    ], className="text-center"),
                    className="menu-card h-100"
                )
            ], width=3),
            
            # DRE
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.I(className="fas fa-chart-line fa-2x text-info"),
                        html.H5("DRE", className="mt-3"),
                        dbc.CardLink("", href="/dre", className="stretched-link")
                    ], className="text-center"),
                    className="menu-card h-100"
                )
            ], width=3),
            
            # Médicos
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.I(className="fas fa-user-md fa-2x text-primary"),
                        html.H5("Médicos", className="mt-3"),
                        dbc.CardLink("", href="/medicos", className="stretched-link")
                    ], className="text-center"),
                    className="menu-card h-100"
                )
            ], width=3),
        ], className="mb-4"),
    ], fluid=True)

# Layout principal do app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback para navegação
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    try:
        if pathname == '/atendimentos':
            return atendimentos.layout()
        elif pathname == '/agendamentos':
            return html.H1("Página de Agendamentos em Construção")
        elif pathname == '/convenios':
            return html.H1("Página de Convênios em Construção")
        elif pathname == '/contas-pagar':
            return html.H1("Página de Contas a Pagar em Construção")
        elif pathname == '/contas-receber':
            return html.H1("Página de Contas a Receber em Construção")
        elif pathname == '/dre':
            return html.H1("Página de DRE em Construção")
        elif pathname == '/clientes':
            return html.H1("Página de Clientes em Construção")
        elif pathname == '/medicos':
            return html.H1("Página de Médicos em Construção")
        elif pathname == '/' or pathname is None:
            return create_home_layout()
        else:
            return html.H1("404 - Página não encontrada")
    except Exception as e:
        print(f"Error in display_page: {str(e)}")
        return html.Div([
            html.H1("Erro ao carregar a página"),
            html.P(str(e))
        ])

if __name__ == '__main__':
    print("Iniciando servidor...")
    app.run_server(debug=True, port=8050)