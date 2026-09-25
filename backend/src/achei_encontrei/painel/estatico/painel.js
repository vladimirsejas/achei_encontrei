// Achei, Encontrei — painel do balcão.
// Busca os dados na API e escreve tudo em linguagem simples. Sem bibliotecas externas.

const CATEGORIAS = {
  DOCUMENTO: "Documento",
  ELETRONICO: "Eletrônico",
  CARTEIRA: "Carteira",
  CHAVE: "Chave",
  BOLSA_MOCHILA: "Bolsa ou mochila",
  ROUPA_ACESSORIO: "Roupa ou acessório",
  OUTRO: "Outro",
};

const EXIGENCIA_POR_RISCO = {
  BAIXO: "Objeto de risco baixo: basta a pessoa descrever o objeto.",
  MEDIO: "Objeto de risco médio: a pessoa precisa descrever detalhes que não estão à vista.",
  ALTO: "Documento: além da descrição, confira um documento de identidade de quem está retirando.",
};

const estado = {
  instituicao: null,
  operadorId: null,
  achados: [],      // todos os achados da instituição
  custodias: {},    // achado_id -> custódia (local onde está guardado)
  prazos: {},       // achado_id -> situação do prazo
  relatorio: null,
  eventos: [],
  achadoEmAcao: null,
};

// ---------------------------------------------------------------- utilidades

const $ = (seletor) => document.querySelector(seletor);

function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto ?? "";
  return div.innerHTML;
}

function dataBR(iso) {
  const [ano, mes, dia] = iso.slice(0, 10).split("-");
  return `${dia}/${mes}/${ano}`;
}

function horaBR(isoCompleto) {
  // O servidor grava em UTC. O SQLite devolve a hora sem a marca de fuso;
  // sem o "Z", o navegador leria como hora local e mostraria 3 horas adiantado.
  const temFuso = /[zZ]|[+-]\d{2}:?\d{2}$/.test(isoCompleto);
  const d = new Date(temFuso ? isoCompleto : `${isoCompleto}Z`);
  return d.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

function hojeISO() {
  const d = new Date();
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}

function plural(n, singular, pluralTexto) {
  return `${n} ${n === 1 ? singular : pluralTexto}`;
}

async function api(caminho, opcoes = {}) {
  const resposta = await fetch(caminho, {
    headers: { "Content-Type": "application/json" },
    ...opcoes,
  });
  const corpo = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    let mensagem = corpo.detail;
    if (Array.isArray(mensagem)) mensagem = mensagem.map((e) => e.msg).join(" ");
    throw new Error(mensagem || "Não foi possível completar a operação.");
  }
  return corpo;
}

function avisar(texto) {
  const aviso = $("#aviso");
  aviso.textContent = texto;
  aviso.classList.add("visivel");
  clearTimeout(avisar.tempo);
  avisar.tempo = setTimeout(() => aviso.classList.remove("visivel"), 3500);
}

// ---------------------------------------------------------------- carregar dados

async function iniciar() {
  preencherCategorias();
  $("#campo-data").value = hojeISO();
  $("#campo-data").max = hojeISO();

  const instituicoes = await api("/instituicoes");
  if (instituicoes.length === 0) {
    $("#nome-instituicao").textContent = "Nenhuma instituição cadastrada";
    $("#manchete").textContent = "O balcão ainda está vazio.";
    $("#manchete-sub").textContent =
      "Para criar um balcão de demonstração, rode no terminal: uv run python scripts/popular_demo.py";
    return;
  }

  const pedida = new URLSearchParams(location.search).get("instituicao");
  estado.instituicao = instituicoes.find((i) => i.id === pedida) || instituicoes[0];

  if (instituicoes.length > 1) {
    const escolha = $("#escolha-instituicao");
    escolha.hidden = false;
    escolha.innerHTML = instituicoes
      .map((i) => `<option value="${i.id}">${escapar(i.nome)}</option>`)
      .join("");
    escolha.value = estado.instituicao.id;
    escolha.onchange = () => { location.search = `?instituicao=${escolha.value}`; };
  }
  $("#nome-instituicao").textContent = estado.instituicao.nome;

  const operadores = await api(`/instituicoes/${estado.instituicao.id}/operadores`);
  const escolhaOperador = $("#escolha-operador");
  escolhaOperador.innerHTML = operadores
    .map((o) => `<option value="${o.id}">${escapar(o.nome)}</option>`)
    .join("");
  estado.operadorId = operadores[0]?.id ?? null;
  escolhaOperador.onchange = () => { estado.operadorId = escolhaOperador.value; };

  await recarregar();
}

async function recarregar() {
  const id = estado.instituicao.id;
  // A rotina diária de prazos: emite os alertas que ainda não foram emitidos.
  await api("/prazos/verificar", { method: "POST" }).catch(() => {});

  const [achados, prazos, relatorio, eventos] = await Promise.all([
    api(`/instituicoes/${id}/achados`),
    api(`/instituicoes/${id}/prazos`),
    api(`/instituicoes/${id}/relatorio`),
    api(`/eventos?instituicao_id=${id}&limite=1000`),
  ]);
  estado.achados = achados;
  estado.prazos = Object.fromEntries(prazos.map((p) => [p.achado_id, p]));
  estado.relatorio = relatorio;
  estado.eventos = eventos;

  const abertos = achados.filter((a) => estado.prazos[a.id]);
  const detalhes = await Promise.all(abertos.map((a) => api(`/achados/${a.id}`)));
  estado.custodias = Object.fromEntries(detalhes.map((d) => [d.id, d.custodia]));

  desenharHoje();
  desenharHistorico();
}

// ---------------------------------------------------------------- hoje no balcão

function textoDoPrazo(prazo) {
  const d = prazo.dias_restantes;
  if (prazo.situacao === "VENCIDO") {
    return { classe: "vencido", carimbo: `Vencido há ${plural(-d, "dia", "dias")}` };
  }
  if (d === 0) return { classe: "proximo", carimbo: "Vence hoje" };
  if (prazo.situacao === "PROXIMO_DO_LIMITE") {
    return { classe: "proximo", carimbo: `Vence em ${plural(d, "dia", "dias")}` };
  }
  return { classe: "no-prazo", carimbo: `Faltam ${plural(d, "dia", "dias")}` };
}

function desenharHoje() {
  const abertos = estado.achados
    .filter((a) => estado.prazos[a.id])
    .sort((a, b) => estado.prazos[a.id].dias_restantes - estado.prazos[b.id].dias_restantes);

  const vencidos = abertos.filter((a) => estado.prazos[a.id].situacao === "VENCIDO");
  const proximos = abertos.filter((a) => estado.prazos[a.id].situacao === "PROXIMO_DO_LIMITE");

  // Manchete em linguagem simples
  if (abertos.length === 0) {
    $("#manchete").textContent = "Nenhum objeto esperando o dono.";
    $("#manchete-sub").textContent = "Quando alguém entregar um objeto no balcão, registre na aba Registrar objeto.";
  } else {
    $("#manchete").textContent =
      `${plural(abertos.length, "objeto esperando", "objetos esperando")} o dono.`;
    if (vencidos.length) {
      $("#manchete-sub").textContent =
        `${plural(vencidos.length, "já passou", "já passaram")} do prazo legal de 15 dias e ` +
        `${vencidos.length === 1 ? "precisa" : "precisam"} ser levado${vencidos.length === 1 ? "" : "s"} à autoridade.`;
    } else if (proximos.length) {
      $("#manchete-sub").textContent =
        `${plural(proximos.length, "está", "estão")} perto do fim do prazo legal de 15 dias.`;
    } else {
      $("#manchete-sub").textContent = "Todos estão dentro do prazo legal de 15 dias.";
    }
  }

  // Precisa de atenção
  $("#atencao").innerHTML = [...vencidos, ...proximos].map((a) => {
    const p = estado.prazos[a.id];
    const venc = p.situacao === "VENCIDO";
    const frase = venc
      ? `O prazo de <strong>${escapar(a.descricao.toLowerCase())}</strong> terminou em ${dataBR(p.prazo_legal_entrega)}. Leve à autoridade e registre a entrega.`
      : `O prazo de <strong>${escapar(a.descricao.toLowerCase())}</strong> termina em ${dataBR(p.prazo_legal_entrega)}.`;
    const botao = venc
      ? `<button class="botao pequeno" data-acao="autoridade" data-id="${a.id}">Registrar entrega</button>`
      : "";
    return `<div class="alerta ${venc ? "vencido" : ""}"><p>${frase}</p>${botao}</div>`;
  }).join("");

  // Etiquetas
  $("#etiquetas").innerHTML = abertos.length
    ? abertos.map(desenharEtiqueta).join("")
    : `<div class="vazio">O balcão está vazio. Nenhum objeto aguardando.</div>`;

  // Números
  const r = estado.relatorio;
  const taxa = r.taxa_devolucao_percentual;
  $("#numeros").innerHTML = `
    <div><dd>${r.total_registrados}</dd><dt>objetos registrados</dt></div>
    <div><dd>${r.devolvidos}</dd><dt>devolvidos ao dono</dt></div>
    <div><dd>${r.encaminhados_autoridade}</dd><dt>entregues à autoridade</dt></div>
    <div><dd>${taxa === null ? "—" : taxa.toLocaleString("pt-BR") + "%"}</dd>
      <dt>voltaram ao dono${taxa === null ? ' <span class="nota">(ainda sem casos encerrados)</span>' : ""}</dt></div>
  `;
}

function desenharEtiqueta(a) {
  const prazo = textoDoPrazo(estado.prazos[a.id]);
  const custodia = estado.custodias[a.id];
  return `
    <article class="etiqueta">
      <div class="etiqueta-topo">
        <span class="categoria">${CATEGORIAS[a.categoria]}</span>
        <span class="carimbo ${prazo.classe}">${prazo.carimbo}</span>
      </div>
      <h3>${escapar(a.descricao)}</h3>
      <p class="detalhe">Encontrado em ${escapar(a.local_encontrado)}, ${dataBR(a.data_achado)}</p>
      <p class="detalhe">Guardado em ${escapar(custodia?.local_fisico ?? "—")}</p>
      <div class="acoes">
        <button class="botao pequeno" data-acao="devolver" data-id="${a.id}">Devolver ao dono</button>
        <button class="botao pequeno secundario" data-acao="autoridade" data-id="${a.id}">Entregar à autoridade</button>
      </div>
    </article>`;
}

// ---------------------------------------------------------------- histórico

function fraseDoEvento(e, nomeObjeto) {
  const d = e.dados || {};
  switch (e.tipo) {
    case "ACHADO_CRIADO": return `Objeto registrado no balcão (${CATEGORIAS[d.categoria] ?? "objeto"}).`;
    case "CUSTODIA_INICIADA": return `Guardado em ${escapar(d.local_fisico)}.`;
    case "CUSTODIA_TRANSFERIDA": return `Mudou de lugar: ${escapar(d.motivo)}.`;
    case "ACHADEGO_INFORMADO": return "Quem encontrou foi avisado do direito à recompensa (achádego).";
    case "PRAZO_ENTREGA_PROXIMO_DO_LIMITE":
      return d.situacao === "VENCIDO"
        ? "Alerta: o prazo legal de 15 dias terminou."
        : "Alerta: o prazo legal de 15 dias está chegando ao fim.";
    case "VERIFICACAO_APROVADA": return "O operador conferiu que a pessoa é a dona do objeto.";
    case "DEVOLUCAO_REALIZADA": return "Devolvido ao dono.";
    case "ENTREGA_AUTORIDADE_REGISTRADA": return `Entregue a ${escapar(d.orgao)}.`;
    case "REIVINDICACAO_CONTESTADA": return `Devolução contestada: ${escapar(d.motivo)}.`;
    default: return escapar(e.tipo);
  }
}

function desenharHistorico() {
  const nomes = Object.fromEntries(estado.achados.map((a) => [a.id, a.descricao]));
  const itens = [...estado.eventos].reverse().map((e) => {
    const achadoId = e.entidade === "Achado" ? e.entidade_id : e.dados?.achado_id;
    const objeto = nomes[achadoId];
    return `
      <li>
        <time datetime="${e.ocorrido_em}">${horaBR(e.ocorrido_em)}</time>
        <div>${fraseDoEvento(e)}${objeto ? `<span class="objeto">${escapar(objeto)}</span>` : ""}</div>
      </li>`;
  });
  $("#linha-do-tempo").innerHTML = itens.join("") || "<li>Nada aconteceu ainda.</li>";
}

// ---------------------------------------------------------------- ações

function abrirDevolver(achado) {
  estado.achadoEmAcao = achado;
  const form = $("#form-devolver");
  form.reset();
  $("#devolver-erro").textContent = "";
  $("#devolver-objeto").textContent = achado.descricao;
  $("#devolver-sinais").hidden = !achado.sinais_privados;
  $("#devolver-sinais-texto").textContent = achado.sinais_privados ?? "";
  $("#devolver-exigencia").textContent = EXIGENCIA_POR_RISCO[achado.nivel_risco];
  $("#dialogo-devolver").showModal();
}

function abrirAutoridade(achado) {
  estado.achadoEmAcao = achado;
  const form = $("#form-autoridade");
  form.reset();
  $("#autoridade-erro").textContent = "";
  $("#autoridade-objeto").textContent = achado.descricao;
  $("#dialogo-autoridade").showModal();
}

document.addEventListener("click", (evento) => {
  const alvo = evento.target.closest("[data-acao], [data-aba], [data-fechar]");
  if (!alvo) return;

  if (alvo.dataset.fechar !== undefined) {
    alvo.closest("dialog").close();
    return;
  }
  if (alvo.dataset.aba) {
    mostrarAba(alvo.dataset.aba);
    return;
  }
  const achado = estado.achados.find((a) => a.id === alvo.dataset.id);
  if (!achado) return;
  if (alvo.dataset.acao === "devolver") abrirDevolver(achado);
  if (alvo.dataset.acao === "autoridade") abrirAutoridade(achado);
});

function mostrarAba(nome) {
  document.querySelectorAll(".secao").forEach((s) => { s.hidden = s.id !== nome; });
  document.querySelectorAll(".aba").forEach((b) => {
    if (b.dataset.aba === nome) b.setAttribute("aria-current", "page");
    else b.removeAttribute("aria-current");
  });
}

function dadosDoFormulario(form) {
  const dados = Object.fromEntries(new FormData(form));
  form.querySelectorAll('input[type="checkbox"]').forEach((c) => { dados[c.name] = c.checked; });
  Object.keys(dados).forEach((k) => { if (dados[k] === "") delete dados[k]; });
  return dados;
}

$("#form-devolver").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const achado = estado.achadoEmAcao;
  try {
    await api(`/achados/${achado.id}/devolucao`, {
      method: "POST",
      body: JSON.stringify({ operador_id: estado.operadorId, ...dadosDoFormulario(evento.target) }),
    });
    $("#dialogo-devolver").close();
    avisar(`Devolvido ao dono: ${achado.descricao}`);
    await recarregar();
  } catch (erro) {
    $("#devolver-erro").textContent = erro.message;
  }
});

$("#form-autoridade").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const achado = estado.achadoEmAcao;
  try {
    await api(`/achados/${achado.id}/entrega-autoridade`, {
      method: "POST",
      body: JSON.stringify({ operador_id: estado.operadorId, ...dadosDoFormulario(evento.target) }),
    });
    $("#dialogo-autoridade").close();
    avisar(`Entrega registrada: ${achado.descricao}`);
    await recarregar();
  } catch (erro) {
    $("#autoridade-erro").textContent = erro.message;
  }
});

$("#form-registrar").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const form = evento.target;
  try {
    const novo = await api(`/instituicoes/${estado.instituicao.id}/achados`, {
      method: "POST",
      body: JSON.stringify({ operador_id: estado.operadorId, ...dadosDoFormulario(form) }),
    });
    form.reset();
    $("#campo-data").value = hojeISO();
    avisar(`Objeto registrado. Prazo legal até ${dataBR(novo.prazo_legal_entrega)}.`);
    await recarregar();
    mostrarAba("hoje");
  } catch (erro) {
    avisar(erro.message);
  }
});

function preencherCategorias() {
  $("#campo-categoria").innerHTML = Object.entries(CATEGORIAS)
    .map(([valor, nome]) => `<option value="${valor}">${nome}</option>`)
    .join("");
}

iniciar().catch((erro) => {
  $("#manchete").textContent = "Não foi possível carregar o balcão.";
  $("#manchete-sub").textContent = erro.message;
});
