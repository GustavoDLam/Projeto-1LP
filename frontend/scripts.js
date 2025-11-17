// URL base da sua API FastAPI
const API_BASE = "http://127.0.0.1:8000";

const API_KEY = "375866160021"

// =========================================
// FUNÇÃO DE MENSAGEM (SUCESSO / ERRO)
// =========================================

/**
 * Mostra uma mensagem na div #mensagem
 * texto: string com a mensagem
 * tipo: "ok" ou "erro" (muda a cor via CSS)
 */
function mostrarMensagem(texto, tipo) {
  const div = document.getElementById("mensagem");
  
  // coloca o texto dentro da div
  div.textContent = texto;

  // remove classes anteriores
  div.classList.remove("ok", "erro");
  
  
  // aplica a classe nova, se tiver
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

// =========================================
// BUSCAR LEADS (GET /leads)
// =========================================

/**
 * Chama GET /leads na API e repassa o resultado
 * para a função que desenha a tabela.
 */
async function carregarLeads() {
  try {
    // limpa qualquer mensagem que estivesse na tela
    mostrarMensagem("", ""); 

    // faz a requisição HTTP
    const resposta = await fetch(`${API_BASE}/leads`, {
        method: "GET",
        headers: {
            "X-API-Key": API_KEY
        },
    });

    // só pra debug: ver o status no console
    console.log("Status GET /leads:", resposta.status);
    
    // se NÃO estiver entre 200 e 299, considera erro
    if (!resposta.ok) {
      throw new Error("Erro ao buscar leads (status " + resposta.status + ")");
    }
    
    // converte o corpo da resposta de JSON para objeto/array JS
    const dados = await resposta.json();

    // desenha a tabela na tela com esses dados
    preencherTabela(dados);
  } catch (erro) {
    console.error(erro);
    mostrarMensagem(erro.message || "Erro ao carregar leads", "erro");
  }
}

// =========================================
// DESENHAR A TABELA DE LEADS
// =========================================

/**
 * Recebe um array de leads e monta as linhas da tabela.
 * Cada lead deve ter: id, nome, email, telefone, data_cadastro.
 */
function preencherTabela(leads) {
  // pega o <tbody> da tabela
  const tbody = document.querySelector("#tabela-leads tbody");
  
  // apaga qualquer conteúdo anterior
  tbody.innerHTML = ""; 
  
  // se não for array ou estiver vazio, mostra uma linha única
  if (!Array.isArray(leads) || leads.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 4;
    td.textContent = "Nenhum lead cadastrado ainda.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }
  
  // para cada lead, criamos uma <tr> com 4 colunas
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

// =========================================
// SALVAR NOVO LEAD (POST /lead)
// =========================================

/**
 * Lida com o envio do formulário.
 * Lê os campos, valida, envia para a API e
 * recarrega a lista se der tudo certo.
 */
async function salvarLead(evento) {
  // impede o comportamento padrão do form (recarregar a página)
  evento.preventDefault(); 
  
  // lê os valores dos inputs
  const nome = document.getElementById("nome").value.trim();
  const email = document.getElementById("email").value.trim();
  const telefone = document.getElementById("telefone").value.trim();
  
  // validação bem simples no front
  if (!nome || !email || !telefone) {
    mostrarMensagem("Preencha todos os campos.", "erro");
    return;
  }
  
  // monta o objeto que o backend espera
  const lead = { nome, email, telefone };

  try {
    mostrarMensagem("", "");
    // faz o POST /lead
    const resposta = await fetch(`${API_BASE}/lead`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        // para o POST não estamos exigindo API_KEY no backend,
        // mas se você colocar, é só enviar aqui também:
        // "X-API-Key": API_KEY,
      },
      body: JSON.stringify(lead),
    });

    console.log("Status POST /lead:", resposta.status);

    // se o status for 400 (validação) ou outro erro, cai aqui
    if (!resposta.ok) {
      // tenta ler a mensagem detalhada do backend
      let msgErro = "Erro ao salvar lead (status " + resposta.status + ")";
      try {
        const data = await resposta.json();
        if (data.detail) {
          msgErro = data.detail;
        }
      } catch (e) {
        // se não for JSON, ignora
      }
      throw new Error(msgErro);
    }

    // se chegou aqui, deu tudo certo no servidor
    mostrarMensagem("Lead salvo com sucesso!", "ok");

    // limpa o formulário
    document.getElementById("lead-form").reset();

    // recarrega a lista de leads para incluir o novo
    await carregarLeads();
  } catch (erro) {
    console.error(erro);
    mostrarMensagem(erro.message || "Erro ao salvar lead", "erro");
  }
}

// =========================================
// INICIALIZAÇÃO DA PÁGINA
// =========================================

/**
 * Quando o HTML terminar de carregar, conectamos
 * os eventos (submit do form, clique no botão atualizar)
 * e já buscamos a primeira lista de leads.
 */
document.addEventListener("DOMContentLoaded", () => {
  // formulário
  const form = document.getElementById("lead-form");
  form.addEventListener("submit", salvarLead);

  // botão de atualizar lista
  const btnAtualizar = document.getElementById("btn-atualizar");
  btnAtualizar.addEventListener("click", carregarLeads);

  // carrega a lista na abertura da página
  carregarLeads();
});
