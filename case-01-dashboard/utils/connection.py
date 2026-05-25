"""
connection.py — Módulo de conexão com o banco de dados Supabase (PostgreSQL).

Responsabilidade: fornecer uma função reutilizável que:
  1. Lê as credenciais do arquivo .env via python-dotenv
  2. Abre uma conexão psycopg2 com o Supabase PostgreSQL
  3. Executa uma query SQL e retorna o resultado como pandas.DataFrame
  4. Trata erros de conexão e exibe mensagem amigável

Uso:
    from utils.connection import run_query
    df = run_query("SELECT * FROM public_gold_sales.vendas_temporais LIMIT 10")
"""

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (se existir)
load_dotenv()


def get_connection() -> psycopg2.extensions.connection:
    """
    Abre e retorna uma conexão psycopg2 com o Supabase PostgreSQL.

    Lê as credenciais das variáveis de ambiente:
        SUPABASE_HOST, SUPABASE_PORT, SUPABASE_DB,
        SUPABASE_USER, SUPABASE_PASSWORD

    Returns:
        psycopg2.extensions.connection: Objeto de conexão ativo.

    Raises:
        psycopg2.OperationalError: Se a conexão falhar.
    """
    conn = psycopg2.connect(
        host=os.environ["SUPABASE_HOST"],
        port=int(os.environ.get("SUPABASE_PORT", 5432)),
        dbname=os.environ["SUPABASE_DB"],
        user=os.environ["SUPABASE_USER"],
        password=os.environ["SUPABASE_PASSWORD"],
        sslmode="require",  # Supabase exige SSL
        connect_timeout=10,
    )
    return conn


def run_query(sql: str, params: tuple = None) -> pd.DataFrame:
    """
    Executa uma query SQL no Supabase e retorna um pandas.DataFrame.

    Args:
        sql (str): Query SQL a ser executada.
        params (tuple, optional): Parâmetros para a query parametrizada.

    Returns:
        pd.DataFrame: Resultado da query. DataFrame vazio em caso de erro.
    """
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    except psycopg2.OperationalError as e:
        # Erro de conexão — será tratado na camada de UI (Streamlit)
        raise ConnectionError(
            f"Não foi possível conectar ao banco de dados. "
            f"Verifique suas credenciais no arquivo .env.\n\nDetalhe técnico: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Erro ao executar a query.\n\nDetalhe técnico: {e}"
        ) from e
    finally:
        if conn is not None:
            conn.close()
