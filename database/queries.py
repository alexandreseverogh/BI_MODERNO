import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import List, Optional
import sys
from sqlalchemy.exc import OperationalError, StatementError

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a URL do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERRO: Variável DATABASE_URL não encontrada no arquivo .env")
    print("Diretório atual:", os.getcwd())
    print("Conteúdo do diretório:", os.listdir())
    if os.path.exists('.env'):
        print("Arquivo .env encontrado. Conteúdo:")
        with open('.env', 'r') as f:
            print(f.read())
    else:
        print("Arquivo .env não encontrado!")
    sys.exit(1)

print(f"Conectando ao banco de dados com URL: {DATABASE_URL}")

# Configuração da conexão com o banco de dados
try:
    engine = create_engine(DATABASE_URL)
    # Cria e mantém uma conexão global aberta (com reconexão automática)
    global_conn = None

    def get_conn():
        global global_conn
        try:
            # Testa se a conexão está aberta e funcional
            if global_conn is not None:
                try:
                    global_conn.execute(text("SELECT 1"))
                    return global_conn
                except (OperationalError, StatementError):
                    print("Conexão perdida, tentando reconectar...")
            # (Re)cria a conexão
            global_conn = engine.connect()
            print("Conexão global restabelecida!")
            return global_conn
        except Exception as e:
            print(f"ERRO ao conectar/reconectar ao banco de dados: {str(e)}")
            raise

    result = get_conn().execute(text("SELECT 1"))
    print("Conexão global com o banco de dados estabelecida com sucesso!")
except Exception as e:
    print(f"ERRO ao conectar ao banco de dados: {str(e)}")
    sys.exit(1)

def get_years() -> List[int]:
    """Retorna lista de anos disponíveis ordenados decrescentemente"""
    query = """
    SELECT DISTINCT ano_atendimento as ano
    FROM dados_bi_gore
    ORDER BY ano DESC
    """
    conn = get_conn()
    result = conn.execute(text(query))
    return [row[0] for row in result]

def get_especialidades(anos: Optional[List[str]] = None, meses: Optional[List[str]] = None) -> List[dict]:
    """Retorna lista de especialidades disponíveis no período"""
    query = """
    SELECT DISTINCT especialidade 
    FROM dados_bi_gore 
    WHERE 1=1
    """
    params = {}
    
    if anos:
        query += " AND ano_atendimento = ANY(:anos)"
        params["anos"] = [int(ano) for ano in anos]
    if meses:
        query += " AND mes_atendimento = ANY(:meses)"
        params["meses"] = [int(mes) for mes in meses]
        
    query += " ORDER BY especialidade"
    
    conn = get_conn()
    result = conn.execute(text(query), params)
    return [{"id": row[0], "nome": row[0]} for row in result]

def get_formas_pagamento(anos: Optional[List[str]] = None, meses: Optional[List[str]] = None) -> List[dict]:
    """Retorna lista de formas de pagamento disponíveis no período"""
    query = """
    SELECT DISTINCT forma_de_pagamento 
    FROM dados_bi_gore 
    WHERE 1=1
    """
    params = {}
    
    if anos:
        query += " AND ano_atendimento = ANY(:anos)"
        params["anos"] = [int(ano) for ano in anos]
    if meses:
        query += " AND mes_atendimento = ANY(:meses)"
        params["meses"] = [int(mes) for mes in meses]
        
    query += " ORDER BY forma_de_pagamento"
    
    conn = get_conn()
    result = conn.execute(text(query), params)
    return [{"id": row[0], "nome": row[0]} for row in result]

def get_profissionais(anos: Optional[List[str]] = None, meses: Optional[List[str]] = None) -> List[dict]:
    """Retorna lista de profissionais disponíveis no período"""
    query = """
    SELECT DISTINCT profissional 
    FROM dados_bi_gore 
    WHERE 1=1
    """
    params = {}
    
    if anos:
        query += " AND ano_atendimento = ANY(:anos)"
        params["anos"] = [int(ano) for ano in anos]
    if meses:
        query += " AND mes_atendimento = ANY(:meses)"
        params["meses"] = [int(mes) for mes in meses]
        
    query += " ORDER BY profissional"
    
    conn = get_conn()
    result = conn.execute(text(query), params)
    return [{"id": row[0], "nome": row[0]} for row in result]

def get_segmentos(anos: Optional[List[str]] = None, meses: Optional[List[str]] = None) -> List[dict]:
    """Retorna lista de segmentos disponíveis no período, garantindo unicidade ignorando acentos, espaços e caixa."""
    query = """
    SELECT DISTINCT LOWER(TRIM(UNACCENT(tipo_atendimento))) as tipo_atendimento_normalizado, tipo_atendimento
    FROM dados_bi_gore 
    WHERE 1=1
    """
    params = {}
    
    if anos:
        query += " AND ano_atendimento = ANY(:anos)"
        params["anos"] = [int(ano) for ano in anos]
    if meses:
        query += " AND mes_atendimento = ANY(:meses)"
        params["meses"] = [int(mes) for mes in meses]
        
    query += " GROUP BY tipo_atendimento_normalizado, tipo_atendimento ORDER BY tipo_atendimento"
    
    conn = get_conn()
    result = conn.execute(text(query), params)
    # Usar apenas o primeiro tipo_atendimento para cada tipo_atendimento_normalizado
    vistos = set()
    unicos = []
    for row in result:
        norm = row[0]
        if norm not in vistos:
            unicos.append({"id": row[1], "nome": row[1]})
            vistos.add(norm)
    return unicos

def build_filter_conditions(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> tuple:
    """Constrói as condições WHERE e parâmetros para as queries"""
    conditions = ["1=1"]  # Always true condition as base
    params = {}

    # Only add conditions for non-empty lists
    if anos and len(anos) > 0:
        conditions.append("ano_atendimento = ANY(:anos)")
        params["anos"] = [int(ano) for ano in anos]
    if meses and len(meses) > 0:
        conditions.append("mes_atendimento = ANY(:meses)")
        params["meses"] = [int(mes) for mes in meses]
    if especialidades and len(especialidades) > 0:
        if all(e is None for e in especialidades):
            conditions.append("especialidade IS NULL")
        elif any(e is None for e in especialidades):
            conditions.append("(especialidade = ANY(:especialidades) OR especialidade IS NULL)")
            params["especialidades"] = [e for e in especialidades if e is not None]
        else:
            conditions.append("especialidade = ANY(:especialidades)")
            params["especialidades"] = especialidades
    if formas_pagamento and len(formas_pagamento) > 0:
        if all(f is None for f in formas_pagamento):
            conditions.append("forma_de_pagamento IS NULL")
        elif any(f is None for f in formas_pagamento):
            conditions.append("(forma_de_pagamento = ANY(:formas_pagamento) OR forma_de_pagamento IS NULL)")
            params["formas_pagamento"] = [f for f in formas_pagamento if f is not None]
        else:
            conditions.append("forma_de_pagamento = ANY(:formas_pagamento)")
            params["formas_pagamento"] = formas_pagamento
    if profissionais and len(profissionais) > 0:
        if all(p is None for p in profissionais):
            conditions.append("profissional IS NULL")
        elif any(p is None for p in profissionais):
            conditions.append("(profissional = ANY(:profissionais) OR profissional IS NULL)")
            params["profissionais"] = [p for p in profissionais if p is not None]
        else:
            conditions.append("profissional = ANY(:profissionais)")
            params["profissionais"] = profissionais
    if segmentos and len(segmentos) > 0:
        if all(s is None for s in segmentos):
            conditions.append("tipo_atendimento IS NULL")
        elif any(s is None for s in segmentos):
            conditions.append("(tipo_atendimento = ANY(:segmentos) OR tipo_atendimento IS NULL)")
            params["segmentos"] = [s for s in segmentos if s is not None]
        else:
            conditions.append("tipo_atendimento = ANY(:segmentos)")
            params["segmentos"] = segmentos
    if data_inicial:
        conditions.append("data_atendimento >= :data_inicial")
        params["data_inicial"] = data_inicial
    if data_final:
        conditions.append("data_atendimento <= :data_final")
        params["data_final"] = data_final
    return " AND ".join(conditions), params

def get_total_atendimentos(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> int:
    """Retorna o total de atendimentos únicos (codigo_atendimento) com os filtros aplicados"""
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT COUNT(DISTINCT codigo_atendimento) as total
    FROM dados_bi_gore
    WHERE {where_clause}
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    return result.scalar() or 0

def get_valor_total(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> float:
    """Retorna o valor total dos atendimentos com os filtros aplicados"""
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT COALESCE(SUM(valor_total_unico), 0) as total
    FROM dados_bi_gore
    WHERE {where_clause}
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    return float(result.scalar() or 0)

def get_ticket_medio(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None
) -> float:
    """Retorna o ticket médio dos atendimentos com os filtros aplicados"""
    total = get_valor_total(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos
    )
    count = get_total_atendimentos(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos
    )
    return total / count if count > 0 else 0

def get_atendimentos_por_mes(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> dict:
    """Retorna dados de atendimentos agrupados por mês, considerando apenas atendimentos únicos (codigo_atendimento)"""
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT 
        ano_atendimento as ano,
        mes_atendimento as mes,
        COUNT(DISTINCT codigo_atendimento) as total,
        COALESCE(SUM(valor_total_unico), 0) as valor_total
    FROM dados_bi_gore
    WHERE {where_clause}
    GROUP BY ano, mes
    ORDER BY ano, mes
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            'ano': row.ano,
            'mes': row.mes,
            'atendimentos': row.total,
            'valor_total': float(row.valor_total)
        }
        for row in rows
    ]

def get_top_profissionais(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None,
    limit: int = 10
) -> dict:
    """Retorna os top profissionais por número de atendimentos"""
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    params['limit'] = limit
    query = f"""
    SELECT 
        profissional as nome,
        COUNT(*) as total,
        COALESCE(SUM(valor_total_unico), 0) as valor_total
    FROM dados_bi_gore
    WHERE {where_clause}
    GROUP BY profissional
    ORDER BY total DESC
    LIMIT :limit
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            'nome': row.nome,
            'atendimentos': row.total,
            'valor_total': float(row.valor_total)
        }
        for row in rows
    ]

def get_min_max_data_atendimento():
    query = '''
        SELECT MIN(data_atendimento) as min_data, MAX(data_atendimento) as max_data
        FROM dados_bi_gore
    '''
    conn = get_conn()
    result = conn.execute(text(query)).fetchone()
    return result[0], result[1]

def get_atendimentos_por_medico_mes(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> list:
    """
    Retorna dados de atendimentos únicos (codigo_atendimento) agrupados por médico e mês.
    """
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT 
        profissional as nome_medico,
        ano_atendimento as ano,
        mes_atendimento as mes,
        COUNT(DISTINCT codigo_atendimento) as total
    FROM dados_bi_gore
    WHERE {where_clause}
    GROUP BY profissional, ano, mes
    ORDER BY profissional, ano, mes
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            'nome_medico': row.nome_medico,
            'ano': row.ano,
            'mes': row.mes,
            'total': row.total
        }
        for row in rows
    ]

def get_valor_total_por_medico_ano(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> list:
    """
    Retorna o valor total (soma de valor_total_unico) e o total de atendimentos únicos (codigo_atendimento) agrupados por médico e ano.
    """
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT 
        profissional as nome_medico,
        ano_atendimento as ano,
        COALESCE(SUM(valor_total_unico), 0) as valor_total,
        COUNT(DISTINCT codigo_atendimento) as total_atendimentos
    FROM dados_bi_gore
    WHERE {where_clause}
    GROUP BY profissional, ano
    ORDER BY profissional, ano
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            'nome_medico': row.nome_medico,
            'ano': row.ano,
            'valor_total': float(row.valor_total),
            'total_atendimentos': row.total_atendimentos
        }
        for row in rows
    ]

def get_quantidade_total_por_medico_ano(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> list:
    """
    Retorna a quantidade total de atendimentos únicos (codigo_atendimento) agrupada por médico e ano.
    """
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT 
        profissional as nome_medico,
        ano_atendimento as ano,
        COUNT(DISTINCT codigo_atendimento) as quantidade_total
    FROM dados_bi_gore
    WHERE {where_clause}
    GROUP BY profissional, ano
    ORDER BY profissional, ano
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            'nome_medico': row.nome_medico,
            'ano': row.ano,
            'quantidade_total': row.quantidade_total
        }
        for row in rows
    ]

def get_atendimentos_por_procedimento_ano(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> list:
    """
    Retorna o total de atendimentos únicos (codigo_atendimento) agrupados por especialidade (procedimento) e ano.
    """
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT 
        especialidade as procedimento,
        ano_atendimento as ano,
        COUNT(DISTINCT codigo_atendimento) as total
    FROM dados_bi_gore
    WHERE {where_clause}
    GROUP BY especialidade, ano
    ORDER BY especialidade, ano
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            'procedimento': row.procedimento,
            'ano': row.ano,
            'total': row.total
        }
        for row in rows
    ]

def get_atendimentos_por_ano(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> list:
    """
    Retorna o total de atendimentos agrupados por ano, considerando apenas atendimentos únicos (codigo_atendimento).
    """
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT 
        ano_atendimento as ano,
        COUNT(DISTINCT codigo_atendimento) as total
    FROM dados_bi_gore
    WHERE {where_clause}
    GROUP BY ano
    ORDER BY ano
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            'ano': row.ano,
            'total': row.total
        }
        for row in rows
    ]

def get_total_procedimentos(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> int:
    """Retorna o total de procedimentos (soma das ocorrências do campo item) com os filtros aplicados"""
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT COUNT(item) as total
    FROM dados_bi_gore
    WHERE {where_clause}
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    return result.scalar() or 0

def get_total_procedimentos_por_ano(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> list:
    """
    Retorna o total de procedimentos (COUNT(item)) agrupado por ano.
    """
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT 
        ano_atendimento as ano,
        COUNT(item) as total
    FROM dados_bi_gore
    WHERE {where_clause}
    GROUP BY ano
    ORDER BY ano
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            'ano': row.ano,
            'total': row.total
        }
        for row in rows
    ]

def get_procedimentos_por_medico_ano(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> list:
    """
    Retorna a quantidade de procedimentos (COUNT(item)) agrupada por médico e ano.
    """
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
    SELECT 
        profissional as nome_medico,
        ano_atendimento as ano,
        COUNT(item) as total_procedimentos
    FROM dados_bi_gore
    WHERE {where_clause}
    GROUP BY profissional, ano
    ORDER BY profissional, ano
    """
    conn = get_conn()
    result = conn.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            'nome_medico': row.nome_medico,
            'ano': row.ano,
            'total_procedimentos': row.total_procedimentos
        }
        for row in rows
    ]

def get_dados_filtrados(
    anos: Optional[List[str]] = None,
    meses: Optional[List[str]] = None,
    especialidades: Optional[List[str]] = None,
    formas_pagamento: Optional[List[str]] = None,
    profissionais: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
) -> pd.DataFrame:
    """
    Retorna um DataFrame com todas as colunas relevantes já filtradas.
    """
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f'''
        SELECT
            data_atendimento,
            ano_atendimento,
            mes_atendimento,
            profissional,
            item,
            tipo_atendimento,
            forma_de_pagamento,
            valor_total_unico,
            codigo_atendimento,
            especialidade
        FROM dados_bi_gore
        WHERE {where_clause}
    '''
    conn = get_conn()
    print('[DEBUG] SQL:', query)
    print('[DEBUG] Params:', params)
    df = pd.read_sql_query(text(query), conn, params=params)
    return df

def get_dados_agrupados(
    group_fields: list,
    anos: Optional[list] = None,
    meses: Optional[list] = None,
    especialidades: Optional[list] = None,
    formas_pagamento: Optional[list] = None,
    profissionais: Optional[list] = None,
    segmentos: Optional[list] = None,
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None,
    agregacoes: Optional[dict] = None
) -> pd.DataFrame:
    """
    Retorna um DataFrame já agrupado conforme os campos e agregações desejadas.
    group_fields: lista de campos para o GROUP BY (ex: ['ano', 'mes'])
    agregacoes: dict do tipo {'nome_coluna': 'AGG_FUNC'} (ex: {'valor_total_unico': 'SUM', 'codigo_atendimento': 'COUNT(DISTINCT)'})
    """
    # Mapear campos para SQL
    field_map = {
        'ano': "ano_atendimento as ano",
        'mes': "mes_atendimento as mes",
        'profissional': "profissional",
        'especialidade': "especialidade",
        'forma_de_pagamento': "forma_de_pagamento",
        'tipo_atendimento': "tipo_atendimento"
    }
    select_fields = [field_map[f] for f in group_fields]
    group_by_fields = [f.split(' as ')[-1] for f in select_fields]
    # Agregações
    agg_selects = []
    for col, agg in agregacoes.items():
        if agg == 'COUNT(DISTINCT)':
            agg_selects.append(f"COUNT(DISTINCT {col}) as {col}_count_distinct")
        else:
            agg_selects.append(f"{agg}({col}) as {col}_{agg.lower()}")
    select_clause = ', '.join(select_fields + agg_selects)
    group_by_clause = ', '.join(group_by_fields)
    where_clause, params = build_filter_conditions(
        anos, meses, especialidades, formas_pagamento,
        profissionais, segmentos, data_inicial, data_final
    )
    query = f"""
        SELECT {select_clause}
        FROM dados_bi_gore
        WHERE {where_clause}
        GROUP BY {group_by_clause}
        ORDER BY {group_by_clause}
    """
    conn = get_conn()
    print('[DEBUG] SQL:', query)
    print('[DEBUG] Params:', params)
    df = pd.read_sql_query(text(query), conn, params=params)
    return df 