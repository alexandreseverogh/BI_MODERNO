
import psycopg2
from urllib.parse import quote_plus  

try:
   
    raw_password = '@*RGt0W871!d'
    escaped_password = quote_plus(raw_password) 

    conn = psycopg2.connect(
        host='srv659302.hstgr.cloud',
        database='db_gore',
        user='developer',
        password=raw_password 
    )
    print("1. Conexão OK")

    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("2. Query simples OK")

    cur.execute("SELECT COUNT(*) FROM dados_bi_gore")
    count = cur.fetchone()
    print("3. Total de registros:", count[0])

    cur.close()
    conn.close()
    print("4. Conexão fechada")

except Exception as e:
    print("ERRO:", str(e))