import pandas as pd
import os
from sqlalchemy import create_engine, inspect, text
import traceback
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("A variável de ambiente DATABASE_URL não está definida!")

engine = create_engine(DATABASE_URL)

def execute_query(query, params=None):
    """Executa uma query e retorna um DataFrame"""
    print("\n=== INÍCIO DA EXECUÇÃO DA QUERY ===")
    print(f"Query: {query}")
    print(f"Parâmetros: {params}")
    
    try:
        print("Executando query...")
        if params:
            # Converter os parâmetros para o formato correto
            if isinstance(params, tuple) and len(params) > 0:
                # Se os parâmetros são listas, converta para strings separadas por vírgula
                params = tuple(
                    ','.join(map(str, p)) if isinstance(p, (list, tuple)) else str(p)
                    for p in params
                )
            
            print(f"Parâmetros formatados: {params}")
            df = pd.read_sql_query(query, engine, params=params)
        else:
            df = pd.read_sql_query(query, engine)
        
        print(f"Query executada com sucesso. Registros retornados: {len(df)}")
        return df
        
    except Exception as e:
        print(f"ERRO ao executar query: {str(e)}")
        print("Traceback completo:")
        print(traceback.format_exc())
        return pd.DataFrame()
    finally:
        print("=== FIM DA EXECUÇÃO DA QUERY ===\n")

def get_available_years():
    """Retorna lista de anos disponíveis no banco"""
    print("\nBuscando anos disponíveis...")
    query = """
        SELECT DISTINCT 
            EXTRACT(YEAR FROM data_atendimento)::integer as ano
        FROM dados_bi_gore
        ORDER BY ano DESC
    """
    df = execute_query(query)
    if df.empty:
        print("Nenhum ano encontrado")
        return []
    years = [str(int(year)) for year in df['ano'].tolist()]
    print(f"Anos encontrados: {years}")
    return years