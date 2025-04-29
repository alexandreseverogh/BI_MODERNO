from data.database import execute_query
import pandas as pd

def test_data():
    # Teste 1: Anos
    print("\n=== Teste 1: Anos ===")
    query_anos = """
        SELECT DISTINCT 
            EXTRACT(YEAR FROM data_atendimento)::integer as ano 
        FROM dados_bi_gore 
        ORDER BY ano DESC
    """
    df_anos = execute_query(query_anos)
    if not df_anos.empty:
        print("Anos:", df_anos['ano'].tolist())

    # Teste 2: Total
    print("\n=== Teste 2: Total ===")
    query_total = "SELECT COUNT(*) as total FROM dados_bi_gore"
    df_total = execute_query(query_total)
    if not df_total.empty:
        print("Total:", df_total['total'].iloc[0])

    # Teste 3: Amostra
    print("\n=== Teste 3: Amostra ===")
    query_amostra = """
        SELECT 
            data_atendimento,
            COUNT(*) as total
        FROM dados_bi_gore
        GROUP BY data_atendimento
        ORDER BY data_atendimento DESC
        LIMIT 5
    """
    df_amostra = execute_query(query_amostra)
    if not df_amostra.empty:
        print("\nAmostra:")
        print(df_amostra)

if __name__ == "__main__":
    test_data()