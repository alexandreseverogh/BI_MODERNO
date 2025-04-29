import pandas as pd
from sqlalchemy import create_engine
import traceback

def get_db_config():
    return {
        'host': 'localhost',
        'database': 'BI_GORE',
        'user': 'postgres',
        'password': 'postgre123'
    }

def execute_query(query, params=None):
    """Executa uma query e retorna um DataFrame"""
    print("\n=== INÍCIO DA EXECUÇÃO DA QUERY ===")
    print(f"Query: {query}")
    print(f"Parâmetros: {params}")
    
    try:
        config = get_db_config()
        connection_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
        
        print("Criando conexão com o banco...")
        engine = create_engine(connection_string)
        
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