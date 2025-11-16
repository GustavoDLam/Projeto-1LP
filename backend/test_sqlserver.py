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

def execute_non_query(sql: str, params: tuple | None = None):
    """
    Executa um comando que NÃO retorna linhas (INSERT, UPDATE, DELETE, CREATE, etc.).
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
    Executa um SELECT e retorna todas as linhas.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()

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

'''
    Create Table inicialmente ultilizado para criar a tabela
    Nao funcionou e criei manualmente no SSMS
    Nao ha nescessidade de ultilizar de novo.
'''
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
        execute_non_query(sql)
        print("✅ Tabela Leads verificada/criada com sucesso.")
    except Exception as e:
        print("❌ Erro ao criar/verificar a tabela Leads:")
        print(e)

def list_leads():
    """
    Lista todos os leads da tabela Leads.
    """
    sql = """
    SELECT Id, Nome, Email, Telefone, DataCadastro
    FROM Leads
    ORDER BY Id DESC;
    """

    try:
        rows = execute_query(sql)
        if not rows:
            print("📋 Nenhum lead encontrado.")
            return

        print("📋 Leads cadastrados:")
        for row in rows:
            lead_id, nome, email, telefone, data_cad = row
            print(f"[{lead_id}] {nome} | {email} | {telefone} | {data_cad}")
    except Exception as e:
        print("❌ Erro ao listar leads:")
        print(e)

def insert_lead(nome: str, email: str, telefone: str | None = None):
    sql = """
    INSERT INTO Leads (Nome, Email, Telefone)
    VALUES (?, ?, ?);
    """
    try:
        execute_non_query(sql, (nome, email, telefone))
        print(f"✅ Lead '{nome}' inserido com sucesso.")
    except Exception as e:
        print("❌ Erro ao inserir lead:")
        print(e)

def validar_email(email: str) -> bool:
    # versão bem simples: precisa ter "@" e pelo menos um "."
    if "@" not in email:
        return False
    usuario, dominio = email.split("@", 1)
    if not usuario or "." not in dominio:
        return False
    return True

def validar_telefone(telefone: str) -> bool:
    # tira espaços e traços
    apenas_digitos = "".join(ch for ch in telefone if ch.isdigit())

    # aqui você define a regra — exagerando um pouco:
    # mínimo 9, máximo 15 dígitos, por exemplo
    if len(apenas_digitos) < 9 or len(apenas_digitos) > 15:
        return False

    return True

if __name__ == "__main__":
    test_connection()
    create_table_leads()

    while True:
        print("\n--- Cadastro de lead manual ---")
        nome = input("Nome (ou ENTER para sair): ").strip()
        if not nome:
            print("Saindo do cadastro de leads.")
            break

        email = input("Email: ").strip()
        if not validar_email(email):
            print("❌ Email inválido, tente novamente.")
            continue

        telefone_input = input("Telefone (opcional): ").strip()
        telefone = telefone_input or None
        if telefone and not validar_telefone(telefone):
            print("❌ Telefone inválido, tente novamente.")
            continue

        insert_lead(nome, email, telefone)