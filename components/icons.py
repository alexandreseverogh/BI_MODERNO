from dash import html

def create_menu_icon(icon_class, text):
    """
    Cria um ícone de menu com texto abaixo
    icon_class: classe do Font Awesome (ex: 'fa-solid fa-chart-line')
    text: texto que aparece abaixo do ícone
    """
    return html.Div([
        html.I(className=icon_class),
        html.Span(text, className="menu-text")
    ], className="menu-icon")