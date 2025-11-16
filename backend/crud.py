# backend/crud.py
# operações de banco (CRUD) para Leads

from database import execute_non_query, execute_query


# --------- CRIAÇÃO DE ESTRUTURA -------

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
    execute_non_query(sql)


# --------- CRUD DE LEADS ---------

def insert_lead(nome: str, email: str, telefone: str | None = None) -> None:
    """
    Insere um lead na tabela Leads.
    """
    sql = """
    INSERT INTO Leads (Nome, Email, Telefone)
    VALUES (?, ?, ?);
    """
    params = (nome, email, telefone)
    execute_non_query(sql, params)


def get_leads():

    """
    Busca todos os leads.
    Retorna lista de tuplas:
    (Id, Nome, Email, Telefone, DataCadastro)
    """
    sql = """
    SELECT Id, Nome, Email, Telefone, DataCadastro
    FROM Leads
    ORDER BY Id DESC;
    """
    return execute_query(sql)


def get_lead_by_id(lead_id: int):
    """
    Busca um lead específico pelo Id.
    """
    sql = """
    SELECT Id, Nome, Email, Telefone, DataCadastro
    FROM Leads
    WHERE Id = ?;
    """
    rows = execute_query(sql, (lead_id,))
    return rows[0] if rows else None


def delete_lead(lead_id: int) -> None:
    """
    Remove um lead pelo Id.
    """
    sql = "DELETE FROM Leads WHERE Id = ?;"
    execute_non_query(sql, (lead_id,))