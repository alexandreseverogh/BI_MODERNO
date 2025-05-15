# test_simple.py
import psycopg2

def test_simple_connection():
    try:
        # Tentar conexão básica
       conn = psycopg2.connect(
        host='srv659302.hstgr.cloud',
        database='db_gore',
        user='developer',
        password=raw_password 
    )
        
        # Testar uma query simples sem caracteres especiais
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print("Conexão básica OK - Resultado:", result)
        
        # Testar uma query real mas simples
        cursor.execute("SELECT COUNT(*) FROM dados_bi_gore")
        count = cursor.fetchone()
        print("Total de registros:", count[0])
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print("Erro:", str(e))

if __name__ == "__main__":
    test_simple_connection()