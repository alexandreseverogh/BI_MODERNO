from data.database import execute_query

# Teste 1: Verificar se a tabela existe e tem dados
query1 = """
SELECT COUNT(*) as total
FROM dados_bi_gore;
"""

# Teste 2: Verificar a estrutura dos dados
query2 = """
SELECT data_atendimento, COUNT(*) as total
FROM dados_bi_gore
GROUP BY data_atendimento
ORDER BY data_atendimento DESC
LIMIT 5;
"""

print("=== Teste 1: Contagem total de registros ===")
try:
    result1 = execute_query(query1)
    print(f"Total de registros: {result1['total'].iloc[0]}")
except Exception as e:
    print(f"Erro ao executar teste 1: {str(e)}")

print("\n=== Teste 2: Últimos 5 dias de atendimento ===")
try:
    result2 = execute_query(query2)
    print(result2)
except Exception as e:
    print(f"Erro ao executar teste 2: {str(e)}")