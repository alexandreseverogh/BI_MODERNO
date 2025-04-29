# test_minimal.py

import psycopg2

try:
    # Testar conexão com o nome correto do banco
    conn = psycopg2.connect(
        host='localhost',
        database='BI_GORE',  # Nome correto em maiúsculas como mostrado no \l
        user='postgres',
        password='postgre123'
    )
    print("1. Conexão OK")
    
    # Testar query simples
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("2. Query simples OK")
    
    # Testar contagem
    cur.execute("SELECT COUNT(*) FROM dados_bi_gore")
    count = cur.fetchone()
    print("3. Total de registros:", count[0])
    
    cur.close()
    conn.close()
    print("4. Conexão fechada")
    
except Exception as e:
    print("ERRO:", str(e))