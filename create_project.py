import os
import shutil

def create_project_structure(base_path):
    # Estrutura de diretórios e arquivos
    structure = {
        'assets': {
            'css': ['style.css'],
            'img': []
        },
        'components': {
            '__init__.py': '',
            'navbar.py': '',
            'filters.py': '',
            'cards.py': ''
        },
        'layouts': {
            '__init__.py': '',
            'home.py': '',
            'atendimentos.py': '',
            'agendamentos.py': '',
            'convenios.py': '',
            'contas_pagar.py': '',
            'contas_receber.py': '',
            'dre.py': '',
            'clientes.py': ''
        },
        'callbacks': {
            '__init__.py': '',
            'atendimentos_callbacks.py': '',
            'agendamentos_callbacks.py': '',
            'convenios_callbacks.py': ''
        },
        'data': {
            '__init__.py': '',
            'database.py': ''
        },
        'utils': {
            '__init__.py': '',
            'helpers.py': ''
        }
    }

    # Criar diretórios e arquivos
    for dir_name, contents in structure.items():
        dir_path = os.path.join(base_path, dir_name)
        
        # Criar diretório se não existir
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✅ Criado diretório: {dir_path}")

        # Se for um dicionário, criar subdiretórios/arquivos
        if isinstance(contents, dict):
            for sub_name, sub_contents in contents.items():
                sub_path = os.path.join(dir_path, sub_name)
                
                # Se sub_contents for uma lista, é um diretório
                if isinstance(sub_contents, list):
                    if not os.path.exists(sub_path):
                        os.makedirs(sub_path)
                        print(f"✅ Criado subdiretório: {sub_path}")
                    
                    # Criar arquivos dentro do subdiretório
                    for file_name in sub_contents:
                        file_path = os.path.join(sub_path, file_name)
                        if not os.path.exists(file_path):
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write('/* Estilos personalizados */\n')
                            print(f"✅ Criado arquivo: {file_path}")
                
                # Se não for lista, é um arquivo
                else:
                    if not os.path.exists(sub_path):
                        with open(sub_path, 'w', encoding='utf-8') as f:
                            f.write('# Arquivo gerado automaticamente\n')
                        print(f"✅ Criado arquivo: {sub_path}")

    # Criar arquivos principais
    main_files = {
        'app.py': '''import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

server = app.server
''',
        'index.py': '''from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from components.navbar import create_navbar

app.layout = html.Div([
    create_navbar(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

if __name__ == '__main__':
    app.run_server(debug=True)
''',
        'requirements.txt': '''dash==2.14.2
dash-bootstrap-components==1.5.0
pandas==2.1.4
plotly==5.18.0
psycopg2==2.9.9
'''
    }

    for file_name, content in main_files.items():
        file_path = os.path.join(base_path, file_name)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Criado arquivo: {file_path}")

if __name__ == "__main__":
    base_path = r"C:\falcao\GORE"
    create_project_structure(base_path)
    print("\n✨ Estrutura do projeto criada com sucesso!")