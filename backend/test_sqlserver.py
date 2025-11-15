import os
import pyodbc
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

def get_connection():
    # Lê variáveis de ambiente
    server = os.getenv("DB_SERVER", "localhost")
    port = os.getenv("DB_PORT", "1433")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    encrypt = os.getenv("DB_ENCRYPT", "yes")
    trust = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

    # Monta a connection string
    conn_str = (
        "DRIVER={" + driver + "};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust};"
    )

    # Debug opcional (só pra conferir – sem senha!)
    print("🔌 Usando connection string (sem senha):")
    print(conn_str.replace(password, "***"))

    return pyodbc.connect(conn_str)

def test_connection():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION;")
            row = cursor.fetchone()
            print("✅ Conectado com sucesso ao SQL Server!")
            print("Versão do SQL Server:")
            print(row[0])
    except Exception as e:
        print("❌ Erro ao conectar no SQL Server:")
        print(e)

def create_table_leads():
    """
    Cria a tabela Leads se ela ainda não existir.
    """
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

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            print("✅ Tabela Leads verificada/criada com sucesso.")
    except Exception as e:
        print("❌ Erro ao criar/verificar a tabela Leads:")
        print(e)

if __name__ == "__main__":
    test_connection()
    create_table_leads()