# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_table_leads, insert_lead, get_leads

app = FastAPI(title="API de Leads da Landing Page")

# --------- MODELOS (entrada/saída) ---------

class LeadIn(BaseModel):
    nome: str
    email: str
    telefone: str | None = None


class LeadOut(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str | None = None
    data_cadastro: str


# --------- VALIDAÇÕES SIMPLES ---------

def validar_email(email: str) -> bool:
    # validação bem simples só pra não aceitar coisa MUITO errada
    if "@" not in email:
        return False
    usuario, dominio = email.split("@", 1)
    if not usuario or "." not in dominio:
        return False
    return True


def validar_telefone(telefone: str) -> bool:
    apenas_digitos = "".join(ch for ch in telefone if ch.isdigit())
    return 9 <= len(apenas_digitos) <= 15


# --------- EVENTO DE STARTUP ---------

@app.on_event("startup")
def startup():
    # garante que a tabela existe quando o servidor sobe
    create_table_leads()


# --------- ROTAS ---------

@app.get("/")
def raiz():
    return {"message": "API de Leads rodando. Use POST /lead para cadastrar."}


@app.post("/lead")
def criar_lead(lead: LeadIn):
    # validações básicas
    if not lead.nome.strip():
        raise HTTPException(status_code=400, detail="Nome é obrigatório.")

    if not validar_email(lead.email):
        raise HTTPException(status_code=400, detail="Email inválido.")

    if lead.telefone and not validar_telefone(lead.telefone):
        raise HTTPException(status_code=400, detail="Telefone inválido.")

    # se chegou aqui, está tudo ok
    insert_lead(lead.nome, lead.email, lead.telefone)
    return {"message": "Lead cadastrado com sucesso!"}


@app.get("/leads", response_model=list[LeadOut])
def listar_leads():
    rows = get_leads()
    resultado: list[LeadOut] = []

    for row in rows:
        lead_id, nome, email, telefone, data_cad = row
        resultado.append(
            LeadOut(
                id=lead_id,
                nome=nome,
                email=email,
                telefone=telefone,
                data_cadastro=str(data_cad),
            )
        )

    return resultado
