from pydantic import BaseModel

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