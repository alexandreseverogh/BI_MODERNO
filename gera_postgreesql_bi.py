import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import register_adapter, AsIs
import sys
import numpy as np
from io import StringIO

def adapt_numpy_types():
    def adapt_numpy_float64(numpy_float64):
        return AsIs(str(numpy_float64))
    def adapt_numpy_int64(numpy_int64):
        return AsIs(str(numpy_int64))
    
    register_adapter(np.float64, adapt_numpy_float64)
    register_adapter(np.int64, adapt_numpy_int64)

def excel_to_postgresql(excel_file, table_name, db_params):
    try:
        print("🔹 Lendo a planilha Excel...")
        df = pd.read_excel(excel_file, engine='openpyxl')
        
        adapt_numpy_types()
        
        print("🔹 Sanitizando nomes das colunas...")
        def sanitize_column(name):
            name = str(name).strip().lower()
            replacements = {
                ' ': '_', '/': '_', '(': '', ')': '',
                '%': 'porc', '$': 'valor', '@': 'at',
                'ã': 'a', 'ç': 'c', 'á': 'a', 'é': 'e',
                'í': 'i', 'ó': 'o', 'ú': 'u'
            }
            for old, new in replacements.items():
                name = name.replace(old, new)
            return name[:63]
        
        df.columns = [sanitize_column(col) for col in df.columns]

        # Identificar colunas que devem ser numéricas com base no nome
        valor_columns = [col for col in df.columns if 'valor' in col.lower()]
        
        # Converter colunas de valor para numeric
        for col in valor_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        print("🔹 Limpando caracteres inválidos...")
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else '')
        
        print("🔹 Conectando ao banco de dados PostgreSQL...")
        conn = psycopg2.connect(
            dbname=db_params['database'],
            user=db_params['user'],
            password=db_params['password'],
            host=db_params['host']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("🔹 Criando a tabela (caso não exista)...")
        columns = []
        for col in df.columns:
            dtype = df[col].dtype
            if col in valor_columns:
                # Campos de valor usarão NUMERIC(15,2) para maior precisão
                pg_type = 'NUMERIC(15,2)'
            elif pd.api.types.is_integer_dtype(dtype):
                pg_type = 'INTEGER'
            elif pd.api.types.is_float_dtype(dtype):
                pg_type = 'NUMERIC(15,2)'
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                pg_type = 'TIMESTAMP'
            else:
                pg_type = 'TEXT'
            columns.append(sql.Identifier(col) + sql.SQL(' ') + sql.SQL(pg_type))
        
        # Primeiro, dropar a tabela se ela existir
        drop_table = sql.SQL("DROP TABLE IF EXISTS {};").format(sql.Identifier(table_name))
        cursor.execute(drop_table)
        
        # Criar a nova tabela
        create_table = sql.SQL("CREATE TABLE {} ({});").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(columns)
        )
        cursor.execute(create_table)
        
        print("🔹 Inserindo os dados na tabela...")
        buffer = StringIO()
        df.to_csv(buffer, sep='\t', header=False, index=False)
        buffer.seek(0)
        
        cursor.copy_expert(
            sql.SQL("COPY {} FROM STDIN WITH (FORMAT CSV, DELIMITER '\t', NULL '')")
            .format(sql.Identifier(table_name)),
            buffer
        )
        
        print(f"✅ Sucesso! Tabela '{table_name}' criada com {len(df)} registros.")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}", file=sys.stderr)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)
    finally:
        if 'conn' in locals():
            conn.close()

def get_db_config():
    return {
        'excel_file': r'C:\falcao\GORE\BI - GORE.xlsx',  # Caminho atualizado
        'table_name': 'dados_bi_gore',
        'db_params': {
            'host': 'localhost',
            'database': 'BI_GORE',
            'user': 'postgres',
            'password': 'postgre123'
        }
    }

# EXECUÇÃO
if __name__ == "__main__":
    config = get_db_config()
    excel_to_postgresql(config['excel_file'], config['table_name'], config['db_params'])
