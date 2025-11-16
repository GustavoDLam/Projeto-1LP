# backend/database.py
# conexão + helpers genéricos
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()  # lê o .env da pasta backend

# ---------------- CONEXÃO ----------------

def get_connection():
    server = os.getenv("DB_SERVER", "localhost")
    port = os.getenv("DB_PORT", "1433")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    conn_str = (
        "DRIVER={" + driver + "};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(conn_str)

# ------------- HELPERS GENÉRICOS -------------

def execute_non_query(sql: str, params: tuple | None = None) -> None:
    """
    Executa comandos que NÃO retornam linhas:
    INSERT, UPDATE, DELETE, CREATE TABLE, etc.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()

def execute_query(sql: str, params: tuple | None = None):
    """
    Executa SELECT e retorna todas as linhas (lista de tuplas).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()



    sql = "SELECT @@VERSION;"
    rows = execute_query(sql)
    print("✅ Conectado ao SQL Server:")
    print(rows[0][0])

# ------------- TESTE RÁPIDO (opcional) -------------

def test_connection():
    sql = "SELECT @@VERSION;"
    rows = execute_query(sql)
    print("✅ Conectado ao SQL Server:")
    print(rows[0][0])

if __name__ == "__main__":
    # Se rodar "python database.py", só testa a conexão
    test_connection()
