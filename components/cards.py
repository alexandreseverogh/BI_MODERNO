from dash import html
import dash_bootstrap_components as dbc

def create_metric_card(title, value, previous_value=None, variation=None):
    card_content = [
        html.H6(title, className="card-title text-muted mb-1 text-center"),
        html.H4(value, className="card-value mb-0 text-center")
    ]
    
    if previous_value is not None and variation is not None:
        card_content.extend([
            html.P([
                f"Anterior: {previous_value}",
                html.Span(f" ({variation}%)", 
                         className=f"{'positive' if float(variation) > 0 else 'negative'}")
            ], className="card-previous mb-0 mt-2 text-center")
        ])
    
    return dbc.Card(
        dbc.CardBody(card_content),
        className="metric-card h-100 shadow-sm mx-2"
    )