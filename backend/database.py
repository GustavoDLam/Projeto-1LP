# backend/database.py
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

# ------------- FUNÇÕES ESPECÍFICAS -------------

def test_connection():
    sql = "SELECT @@VERSION;"
    rows = execute_query(sql)
    print("✅ Conectado ao SQL Server:")
    print(rows[0][0])

def create_table_leads():
    sql = """
    IF NOT EXISTS (
        SELECT * FROM sys.tables WHERE name = 'Leads' AND type = 'U'
    )
    BEGIN
        CREATE TABLE Leads (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            Nome NVARCHAR(100) NOT NULL,
            Email NVARCHAR(200) NOT NULL,
            Telefone NVARCHAR(20) NULL,
            DataCadastro DATETIME DEFAULT GETDATE()
        );
    END;
    """
    execute_non_query(sql)

def insert_lead(nome: str, email: str, telefone: str | None = None):
    sql = """
    INSERT INTO Leads (Nome, Email, Telefone)
    VALUES (?, ?, ?);
    """
    params = (nome, email, telefone)
    execute_non_query(sql, params)

def get_leads():
    """
    Retorna todos os leads como lista de tuplas:
    (Id, Nome, Email, Telefone, DataCadastro)
    """
    sql = """
    SELECT Id, Nome, Email, Telefone, DataCadastro
    FROM Leads
    ORDER BY Id DESC;
    """
    return execute_query(sql)

# ------------- TESTE RÁPIDO (opcional) -------------

if __name__ == "__main__":
    test_connection()
    create_table_leads()
    print("Tabela Leads verificada/criada com sucesso.")
    for row in get_leads() or []:
        print(row)
