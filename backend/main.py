# backend/main.py 
# rotas FastAPI
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware

from schemas import LeadIn, LeadOut
from crud import (create_table_leads, insert_lead, get_leads, get_lead_by_id, delete_lead)

app = FastAPI(title="API de Leads da Landing Page")

# --------- CORS PARA DESENVOLVIMENTO ---------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # em produção: restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/leads", response_model = list[LeadOut])
def listar_leads(limit: int = Query(50, gt = 0, le = 100), offset: int = Query(0, ge = 0)):

    """
    Lista leads com paginação.

    - limit: quantos registros retornar (1 a 100).
    - offset: a partir de qual posição (0 = desde o início).
    """
    rows = get_leads(limit = limit, offset = offset)
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

@app.get("/leads/{lead_id}", response_model = LeadOut)
def obter_lead(lead_id: int = Path(..., gt = 0)):
    row = get_lead_by_id(lead_id)
    if not row:
        raise HTTPException(status_code = 404, detail = "Lead não encontrado")
    
    lead_id, nome, email, telefone, data_cad = row
    return LeadOut(id = lead_id, nome = nome, email = email, telefone = telefone, data_cadastro = str(data_cad))

@app.delete("/leads/{lead_id}")
def remover_lead(lead_id: int = Path(..., gt = 0)):
    row = get_lead_by_id(lead_id)
    if not row:
        raise HTTPException(status_code = 404, detail = "Lead não encontrado")
    
    delete_lead(lead_id)
    return {"message": f"Lead {lead_id} removido com sucesso" }