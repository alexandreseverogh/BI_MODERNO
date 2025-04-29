import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carregar as variáveis de ambiente
load_dotenv()

# Obter a URL do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERRO: DATABASE_URL não encontrado no arquivo .env")
    exit(1)

print(f"Conectando ao banco de dados: {DATABASE_URL}")

try:
    # Criar a conexão
    engine = create_engine(DATABASE_URL)
    
    # Executar o comando para criar a extensão
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))
        conn.commit()
    
    print("✅ Extensão 'unaccent' criada com sucesso!")
    print("Agora você pode executar sua aplicação normalmente.")

except Exception as e:
    print(f"❌ ERRO ao criar a extensão: {str(e)}")
    print("Verifique se você tem permissões de superusuário no banco de dados.") 