import psycopg2
import pandas as pd
from tabulate import tabulate

def get_db_config():
    return {
        'host': 'localhost',
        'database': 'BI_GORE',
        'user': 'postgres',
        'password': 'postgre123'
    }

def check_table_structure():
    # Configuração da conexão
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    
    try:
        # Query para obter a estrutura da tabela
        structure_query = """
            SELECT 
                ordinal_position,
                column_name,
                data_type,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns
            WHERE table_name = 'dados_bi_gore'
            ORDER BY ordinal_position;
        """
        
        # Query para obter uma amostra dos dados
        sample_query = """
            SELECT *
            FROM dados_bi_gore
            LIMIT 5;
        """
        
        # Executar queries
        structure_df = pd.read_sql_query(structure_query, conn)
        sample_df = pd.read_sql_query(sample_query, conn)
        
        # Imprimir resultados
        print("\n=== Estrutura da Tabela dados_bi_gore ===")
        print(tabulate(structure_df, headers='keys', tablefmt='psql', showindex=False))
        
        print("\n=== Amostra de Dados ===")
        print(tabulate(sample_df, headers='keys', tablefmt='psql', showindex=False))
        
        # Retornar os DataFrames para uso posterior se necessário
        return structure_df, sample_df
        
    except Exception as e:
        print(f"Erro ao verificar estrutura da tabela: {str(e)}")
        return None, None
    finally:
        conn.close()

if __name__ == "__main__":
    check_table_structure()