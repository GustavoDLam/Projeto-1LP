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
  // pegamos o botão de atualizar (pode ser null se o HTML mudar, então testamos depois)
  const btnAtualizar = document.getElementById("btn-atualizar");

  try {
    // Se o botão existir, colocamos ele em estado de "carregando"
    if (btnAtualizar) {
      btnAtualizar.disabled = true;              // desabilita o clique
      btnAtualizar.textContent = "Atualizando..."; // muda o texto do botão
    }

    // Mostra uma mensagem temporária enquanto carrega
    mostrarMensagem("Carregando leads...", "ok");

    // Faz a requisição GET para /leads
    const resposta = await fetch(`${API_BASE}/leads`, {
      method: "GET",
      headers: {
        // Header com a chave de API que o backend espera
        "X-API-Key": API_KEY,
      },
    });

    // Só pra debug: ver o status da resposta no console (200, 401, etc.)
    console.log("Status GET /leads:", resposta.status);

    // Se não for status 2xx (200–299), consideramos erro
    if (!resposta.ok) {
      // Criamos um erro com uma mensagem explicando o status
      throw new Error("Erro ao buscar leads (status " + resposta.status + ")");
    }

    // Converte o corpo da resposta de JSON para objeto/array JavaScript
    const dados = await resposta.json();

    // Debug: ver os dados que chegaram da API
    console.log("Leads recebidos da API:", dados);

    // Atualiza a tabela na tela com os dados recebidos
    preencherTabela(dados);

    // Como deu certo, limpamos a mensagem (poderia trocar por "Leads atualizados", se quiser)
    mostrarMensagem("", "");
  } catch (erro) {
    // Se qualquer coisa der errada lá em cima (fetch, status != 200 etc.), cai aqui
    console.error(erro);
    // Mostra a mensagem de erro para o usuário
    mostrarMensagem(erro.message || "Erro ao carregar leads", "erro");
  } finally {
    // O bloco finally SEMPRE roda, tenha dado erro ou não.
    // Ótimo lugar para "desfazer" estados de loading.

    if (btnAtualizar) {
      btnAtualizar.disabled = false;           // reativa o botão
      btnAtualizar.textContent = "Atualizar lista"; // volta o texto original
    }
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
  const tbody = document.querySelector("#tabela-leads tbody");
  tbody.innerHTML = "";

  // Atualiza o contador de leads (texto embaixo do título)
  const spanContador = document.getElementById("contador-leads");
  if (spanContador) {
    const total = Array.isArray(leads) ? leads.length : 0;
    spanContador.textContent =
      total === 0
        ? "Nenhum lead cadastrado"
        : total === 1
        ? "1 lead"
        : `${total} leads`;
  }

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
    tdTelefone.textContent = lead.telefone || "";

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
  // Impede o comportamento padrão do formulário (recarregar a página)
  evento.preventDefault();

  // Pega os valores dos campos e remove espaços extras nas pontas (trim)
  const nome = document.getElementById("nome").value.trim();
  const email = document.getElementById("email").value.trim();
  const telefone = document.getElementById("telefone").value.trim();

  // Pega o botão de salvar para usar no estado de loading
  const btnSalvar = document.getElementById("btn-salvar");

  // Validação básica no front: não deixa enviar se tiver campo vazio
  if (!nome || !email || !telefone) {
    mostrarMensagem("Preencha todos os campos.", "erro");
    return; // sai da função, não continua
  }

  // Monta o objeto que o backend espera no corpo do POST
  const lead = { nome, email, telefone };

  try {
    // Limpa mensagens anteriores
    mostrarMensagem("", "");

    // Coloca o botão em estado de "salvando", se ele existir
    if (btnSalvar) {
      btnSalvar.disabled = true;           // desabilita o botão (evita duplo clique)
      btnSalvar.textContent = "Salvando..."; // muda o texto pra indicar processamento
    }

    // Faz a requisição POST /lead
    const resposta = await fetch(`${API_BASE}/lead`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json", // indica que estamos mandando JSON
        // Se você resolver exigir API_KEY no POST, basta descomentar:
        // "X-API-Key": API_KEY,
      },
      body: JSON.stringify(lead), // converte o objeto JS para JSON (string)
    });

    // Debug: ver status do POST
    console.log("Status POST /lead:", resposta.status);

    // Se não for 2xx, tratamos como erro
    if (!resposta.ok) {
      // Mensagem padrão caso não venha detalhe do backend
      let msgErro = "Erro ao salvar lead (status " + resposta.status + ")";

      try {
        // Tentamos ler o JSON de erro do backend (FastAPI costuma mandar {"detail": "..."} )
        const data = await resposta.json();
        if (data.detail) {
          msgErro = data.detail; // se tiver detail, usamos essa mensagem
        }
      } catch (e) {
        // Se a resposta não for JSON, caímos aqui e mantemos a msgErro padrão
      }

      // Lançamos o erro com a mensagem final (vai cair no catch)
      throw new Error(msgErro);
    }

    // Se chegou aqui, o backend respondeu 2xx (sucesso)
    mostrarMensagem("Lead salvo com sucesso!", "ok");

    // Limpa os campos do formulário
    document.getElementById("lead-form").reset();

    // Recarrega a lista de leads para já mostrar o novo na tabela
    await carregarLeads();
  } catch (erro) {
    // Qualquer erro durante o try cai aqui
    console.error(erro);
    mostrarMensagem(erro.message || "Erro ao salvar lead", "erro");
  } finally {
    // Independente de sucesso ou erro, voltamos o botão ao normal
    if (btnSalvar) {
      btnSalvar.disabled = false;             // reativa o botão
      btnSalvar.textContent = "Salvar lead";  // texto original
    }
  }
}

// Formata o telefone no padrão brasileiro simples: (XX) XXXXX-XXXX
function aplicarMascaraTelefone(valor) {
  // remove tudo que não for número
  const numeros = valor.replace(/\D/g, "").slice(0, 11); // limita a 11 dígitos

  if (numeros.length <= 2) {
    return numeros;
  }

  if (numeros.length <= 7) {
    // (XX) XXXX
    return `(${numeros.slice(0, 2)}) ${numeros.slice(2)}`;
  }

  // (XX) XXXXX-XXXX
  return `(${numeros.slice(0, 2)}) ${numeros.slice(2, 7)}-${numeros.slice(7)}`;
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

  // Input de telefone com máscara
  const inputTelefone = document.getElementById("telefone");
  if (inputTelefone) {
    inputTelefone.addEventListener("input", (event) => {
      const valorOriginal = event.target.value;
      const valorFormatado = aplicarMascaraTelefone(valorOriginal);
      event.target.value = valorFormatado;
    });
  }

  // carrega a lista na abertura da página
  carregarLeads();
});
