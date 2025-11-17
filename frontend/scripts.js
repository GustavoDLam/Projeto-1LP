// URL base da sua API FastAPI
const API_BASE = "http://127.0.0.1:8000";

const API_KEY = "375866160021"

function mostrarMensagem(texto, tipo) {
  const div = document.getElementById("mensagem");
  div.textContent = texto;

  // remove classes anteriores
  div.classList.remove("ok", "erro");

  if (tipo === "ok") {
    div.classList.add("ok");
  } else if (tipo === "erro") {
    div.classList.add("erro");
  }

  // se tiver texto, mostra; se não, esconde
  if (texto) {
    div.style.display = "block";
  } else {
    div.style.display = "none";
  }
}

// Busca os leads no backend com GET /leads
async function carregarLeads() {
  try {
    mostrarMensagem("", ""); // limpa mensagens
    const resposta = await fetch(`${API_BASE}/leads`, {
        method: "GET",
        headers: {
            "X-API-Key": API_KEY
        },
    });

    if (!resposta.ok) {
      throw new Error("Erro ao buscar leads (status " + resposta.status + ")");
    }

    const dados = await resposta.json();
    preencherTabela(dados);
  } catch (erro) {
    console.error(erro);
    mostrarMensagem(erro.message || "Erro ao carregar leads", "erro");
  }
}

// Preenche a tabela com a lista de leads
function preencherTabela(leads) {
  const tbody = document.querySelector("#tabela-leads tbody");
  tbody.innerHTML = ""; // limpa linhas antigas

  if (!Array.isArray(leads) || leads.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 4;
    td.textContent = "Nenhum lead cadastrado ainda.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  leads.forEach((lead, index) => {
    const tr = document.createElement("tr");

    const tdIndex = document.createElement("td");
    tdIndex.textContent = index + 1;

    const tdNome = document.createElement("td");
    tdNome.textContent = lead.nome;

    const tdEmail = document.createElement("td");
    tdEmail.textContent = lead.email;

    const tdTelefone = document.createElement("td");
    tdTelefone.textContent = lead.telefone;

    tr.appendChild(tdIndex);
    tr.appendChild(tdNome);
    tr.appendChild(tdEmail);
    tr.appendChild(tdTelefone);

    tbody.appendChild(tr);
  });
}

// Envia um novo lead com POST /lead
async function salvarLead(evento) {
  evento.preventDefault(); // impede o envio padrão do formulário

  const nome = document.getElementById("nome").value.trim();
  const email = document.getElementById("email").value.trim();
  const telefone = document.getElementById("telefone").value.trim();

  if (!nome || !email || !telefone) {
    mostrarMensagem("Preencha todos os campos.", "erro");
    return;
  }

  const lead = { nome, email, telefone };

  try {
    mostrarMensagem("", "");
    const resposta = await fetch(`${API_BASE}/lead`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
      },
      body: JSON.stringify(lead),
    });

    if (!resposta.ok) {
      throw new Error("Erro ao salvar lead (status " + resposta.status + ")");
    }

    mostrarMensagem("Lead salvo com sucesso!", "ok");

    // limpa o formulário
    document.getElementById("lead-form").reset();

    // recarrega a lista
    await carregarLeads();
  } catch (erro) {
    console.error(erro);
    mostrarMensagem(erro.message || "Erro ao salvar lead", "erro");
  }
}

// Quando a página carregar, conecta os eventos e carrega a lista
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("lead-form");
  form.addEventListener("submit", salvarLead);

  const btnAtualizar = document.getElementById("btn-atualizar");
  btnAtualizar.addEventListener("click", carregarLeads);

  // Carrega a lista de cara
  carregarLeads();
});
