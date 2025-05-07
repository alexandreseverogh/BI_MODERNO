import os
import traceback
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Tenta obter a URL completa do banco
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Se não houver DATABASE_URL, monta a partir das variáveis individuais
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'BI_GORE')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgre123')
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

def criar_e_preencher_ano_mes_dia():
    """
    Cria as colunas ano, mes e dia na tabela dados_bi_gore (se não existirem)
    e preenche os valores extraídos de data_atendimento.
    """
    try:
        conn = engine.connect()
        insp = inspect(engine)
        columns = [col['name'] for col in insp.get_columns('dados_bi_gore')]
        alter_cmds = []
        if 'ano' not in columns:
            alter_cmds.append('ADD COLUMN ano integer')
        if 'mes' not in columns:
            alter_cmds.append('ADD COLUMN mes integer')
        if 'dia' not in columns:
            alter_cmds.append('ADD COLUMN dia integer')
        if alter_cmds:
            alter_sql = f"ALTER TABLE dados_bi_gore {', '.join(alter_cmds)};"
            print(f"Executando: {alter_sql}")
            conn.execute(text(alter_sql))
        # Preencher os valores
        update_sql = """
            UPDATE dados_bi_gore
            SET ano = EXTRACT(YEAR FROM data_atendimento)::integer,
                mes = EXTRACT(MONTH FROM data_atendimento)::integer,
                dia = EXTRACT(DAY FROM data_atendimento)::integer;
        """
        print("Preenchendo colunas ano, mes e dia...")
        conn.execute(text(update_sql))
        print("Colunas ano, mes e dia criadas e preenchidas com sucesso!")
        conn.close()
    except Exception as e:
        print(f"Erro ao criar/preencher colunas: {e}")
        print(traceback.format_exc()) 