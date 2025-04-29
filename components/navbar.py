import dash_bootstrap_components as dbc
from dash import html

def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-user-clock me-2"),
                        "Atendimentos"
                    ],
                    href="/atendimentos",
                    className="nav-link"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-clock me-2"),
                        "Agendamentos"
                    ],
                    href="/agendamentos",
                    className="nav-link"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-credit-card me-2"),
                        "Convênios"
                    ],
                    href="/convenios",
                    className="nav-link"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-money-bill me-2"),
                        "Contas a Pagar"
                    ],
                    href="/contas-pagar",
                    className="nav-link"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-wallet me-2"),
                        "Contas a Receber"
                    ],
                    href="/contas-receber",
                    className="nav-link"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-file-invoice-dollar me-2"),
                        "DRE"
                    ],
                    href="/dre",
                    className="nav-link"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-users me-2"),
                        "Clientes"
                    ],
                    href="/clientes",
                    className="nav-link"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-user-md me-2"),
                        "Médicos"
                    ],
                    href="/medicos",
                    className="nav-link"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fas fa-database me-2"),
                        "Dados Brutos"
                    ],
                    href="/dados-brutos",
                    className="nav-link"
                )
            ),
        ],
        brand=html.Div([
            html.Img(src="/assets/img/logo.png", height="30px", className="me-2"),
            "GORE"
        ], className="navbar-brand"),
        brand_href="/",
        color="dark",
        dark=True,
        className="custom-navbar"
    )
    return navbar