
// --- Agora: valores atuais ---
const estado = document.getElementById("estado");

const CAMPOS = {
  temperatura: { valor: document.getElementById("v_temperatura"), delta: document.getElementById("d_temperatura"), unidade: "°C" },
  humidade: { valor: document.getElementById("v_humidade"), delta: document.getElementById("d_humidade"), unidade: "%" },
};
for (const [nome, c] of Object.entries(CAMPOS)) c.intervalo = document.getElementById(`i_${nome}`);

// mostra a mensagem de estado; em erro limpa os numeros
function mostrarEstado(texto, ok) {
  estado.textContent = texto;
  estado.className = ok ? "estado ok" : "estado erro";

  if (ok) return;
  for (const c of Object.values(CAMPOS)) {
    c.valor.textContent = "--";
    c.delta.textContent = "";
    c.intervalo.textContent = "";
  }
}

// diferenca entre o valor atual e a media, em texto
function textoDelta(atual, media, unidade) {
  const d = atual - media;
  if (Math.abs(d) < 0.05) return "igual a media dos ultimos 15 min";
  return `${d > 0 ? "+" : "-"}${Math.abs(d).toFixed(1)} ${unidade} face a media dos ultimos 15 min`;
}

// vai buscar a ultima leitura e a media e escreve-as na pagina
async function atualizar() {
  try {
    const [r, m] = await Promise.all([fetch("/"), fetch("/media")]);
    const d = await r.json();
    const v = await m.json();

    if (!r.ok) {
      mostrarEstado(d.detail, false);
      return;
    }

    mostrarEstado(`A receber leituras, atualizado as ${new Date().toLocaleTimeString("pt-PT")}`, true);
    for (const [nome, c] of Object.entries(CAMPOS)) {
      c.valor.textContent = d[nome].toFixed(1);
      c.delta.textContent = m.ok ? textoDelta(d[nome], v[nome], c.unidade) : "sem media nos ultimos 15 min";
    }
  } catch (e) {
    mostrarEstado("Sem ligacao ao servidor", false);
  }
}

// o servidor responde com a ultima leitura guardada, por isso 1 s e barato
atualizar();
setInterval(atualizar, 1000);

// minimo e maximo da ultima hora, por baixo da diferenca para a media
async function atualizarUltimaHora() {
  try {
    const r = await fetch("/estatisticas?minutos=60");
    if (!r.ok) return;

    const d = await r.json();
    for (const [nome, c] of Object.entries(CAMPOS)) {
      c.intervalo.textContent = `ultima hora: ${d[nome].min.toFixed(1)} a ${d[nome].max.toFixed(1)} ${c.unidade}`;
    }
  } catch (e) {
    // atualizar() ja avisa que o servidor nao responde
  }
}

atualizarUltimaHora();
setInterval(atualizarUltimaHora, 5000);

// --- Tema claro/escuro ---
const button_state_mode = document.getElementById("darkmode");

// liga ou desliga o modo escuro e ajusta o texto
function aplicarTema(escuro) {
  document.body.classList.toggle("dark", escuro);
  // texto indica a que modo ira mudar
  button_state_mode.textContent = escuro ? "light" : "dark";
}

// getItem devolve null se nunca guardaste nada, e "true" e um texto, nao um booleano
aplicarTema(localStorage.getItem("tema") === "dark");

button_state_mode.addEventListener("click", function () {
  const escuro = !document.body.classList.contains("dark");

  aplicarTema(escuro);
  localStorage.setItem("tema", escuro ? "dark" : "light");
});

// --- Graficos SVG ---
// unidades do viewBox do svg, nao pixeis
const LARGURA = 600;
const ALTURA = 200;
const MARGEM = { cima: 16, direita: 16, baixo: 28, esquerda: 56 };
const SVG_NS = "http://www.w3.org/2000/svg";

// alcance minimo, senao 0,1 °C enche o grafico todo
function escalaY(valores, alcanceMin) {
  let min = Math.min(...valores);
  let max = Math.max(...valores);

  if (max - min < alcanceMin) {
    const meio = (min + max) / 2;
    min = meio - alcanceMin / 2;
    max = meio + alcanceMin / 2;
  }
  return { min, max };
}

// textContent e setAttribute em vez de innerHTML: o texto nunca e lido como HTML
function criar(tag, atributos, texto) {
  const e = document.createElementNS(SVG_NS, tag);

  for (const [nome, valor] of Object.entries(atributos)) e.setAttribute(nome, valor);
  if (texto !== undefined) e.textContent = texto;

  return e;
}

// "2026-11-06 12:54" (UTC) -> "12:54" na hora local
function horaLocal(hora) {
  const d = new Date(hora.replace(" ", "T") + "Z");
  return d.toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" });
}

// desenha uma linha com eixos num svg; valores e horas tem o mesmo tamanho
function desenhar(id, valores, horas, unidade, alcanceMin) {
  const svg = document.getElementById(id);
  svg.replaceChildren();

  // sem leituras, Math.min() da Infinity
  if (valores.length === 0) return;

  const { min, max } = escalaY(valores, alcanceMin);
  const largura = LARGURA - MARGEM.esquerda - MARGEM.direita;
  const altura = ALTURA - MARGEM.cima - MARGEM.baixo;

  // o "|| 1" evita dividir por 0 com um so valor
  const x = i => MARGEM.esquerda + (i * largura) / ((valores.length - 1) || 1);

  // o y do SVG cresce para baixo
  const y = v => MARGEM.cima + altura - ((v - min) / (max - min)) * altura;

  for (const v of [min, (min + max) / 2, max]) {
    svg.append(criar("line", {
      class: "grelha",
      x1: MARGEM.esquerda, x2: LARGURA - MARGEM.direita,
      y1: y(v), y2: y(v),
    }));

    svg.append(criar("text", {
      class: "rotulo",
      x: MARGEM.esquerda - 8, y: y(v),
      "text-anchor": "end", "dominant-baseline": "middle",
    }, `${v.toFixed(1)}${unidade}`));
  }

  // com 1 ou 2 leituras as marcas coincidiam e as horas ficavam sobrepostas
  const ultimo = valores.length - 1;
  const marcas = [[0, "start"]];
  if (ultimo > 0) marcas.push([ultimo, "end"]);
  if (ultimo > 1) marcas.splice(1, 0, [Math.floor(ultimo / 2), "middle"]);

  for (const [i, ancora] of marcas) {
    svg.append(criar("text", {
      class: "rotulo",
      x: x(i), y: ALTURA - 8,
      "text-anchor": ancora,
    }, horaLocal(horas[i])));
  }

  const pontos = valores.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  svg.append(criar("polyline", { class: "linha", points: pontos }));

  // uma polyline com um so ponto nao desenha nada
  if (valores.length === 1) {
    svg.append(criar("circle", { class: "ponto", cx: x(0), cy: y(valores[0]), r: 3 }));
  }
}

// vai buscar os dados a `url` e desenha os graficos
// graficos: [id do svg, campo, unidade, alcance minimo do eixo Y]
async function carregar(url, campoHora, graficos) {
  try {
    const r = await fetch(url);
    if (!r.ok) return;

    const dados = await r.json();
    const horas = dados.map(d => d[campoHora]);

    for (const [id, campo, unidade, alcanceMin] of graficos) {
      desenhar(id, dados.map(d => d[campo]), horas, unidade, alcanceMin);
    }
  } catch (e) {
    // politica: sem ligacao ou erro do servidor, o grafico anterior fica como esta.
    // As linhas de texto (atualizar) ja avisam que o servidor nao responde.
  }
}

const GRAFICOS_ATUAL = [
  ["grafico_temperatura", "temperatura", " °C", 2],
  ["grafico_humidade", "humidade", " %", 5],
];

const GRAFICOS_MEDIA = [
  ["grafico_media_temperatura", "temperatura", " °C", 2],
  ["grafico_media_humidade", "humidade", " %", 5],
];

// o Arduino envia de 5 em 5 s
carregar("/historico?n=60", "hora", GRAFICOS_ATUAL);
setInterval(() => carregar("/historico?n=60", "hora", GRAFICOS_ATUAL), 5000);

// --- Filtros, estatisticas e dia ---
// grupo de botoes onde so um esta ativo. Devolve uma funcao com o botao ativo.
function grupo(seletor, aoMudar) {
  const botoes = document.querySelectorAll(`${seletor} button`);
  let ativo = botoes[0];

  for (const b of botoes) {
    b.addEventListener("click", () => {
      ativo = b;
      for (const o of botoes) o.setAttribute("aria-pressed", o === b);
      aoMudar();
    });
  }
  return () => ativo;
}

const GRAFICOS_DIA = [
  ["grafico_dia_temperatura", "temperatura", " °C", 2],
  ["grafico_dia_humidade", "humidade", " %", 5],
];

// media: o botao escolhe quantos blocos (n) e de quantos minutos cada (passo)
const botaoMedia = grupo("#media .periodos", () => {
  document.getElementById("media_nota").textContent = botaoMedia().dataset.nota;
  carregarMedias();
});

function carregarMedias() {
  const { n, passo } = botaoMedia().dataset;
  carregar(`/medias?n=${n}&passo=${passo}`, "minuto", GRAFICOS_MEDIA);
}

// a media por minuto so muda uma vez por minuto
carregarMedias();
setInterval(carregarMedias, 60000);

// preenche uma tabela de estatisticas (ids prefixo_temperatura_min, ...)
async function preencherEstatisticas(url, prefixo, nota, texto) {
  const celulas = ["temperatura", "humidade"].flatMap(n => ["min", "media", "max"].map(c => [n, c]));

  try {
    const r = await fetch(url);
    const d = await r.json();

    if (!r.ok) {
      nota.textContent = d.detail;
      for (const [n, c] of celulas) document.getElementById(`${prefixo}_${n}_${c}`).textContent = "--";
      return;
    }

    nota.textContent = `${d.leituras} leituras ${texto}`;
    for (const [n, c] of celulas) document.getElementById(`${prefixo}_${n}_${c}`).textContent = d[n][c].toFixed(1);
  } catch (e) {
    // mesma politica dos graficos: o ultimo valor fica, atualizar() ja avisa que o servidor nao responde
  }
}

const botaoPeriodo = grupo("#estatisticas .periodos", () => carregarPeriodo());

function carregarPeriodo() {
  const b = botaoPeriodo();
  preencherEstatisticas(`/estatisticas?minutos=${b.dataset.minutos}`, "periodo", document.getElementById("stats_n"), `nos ultimos ${b.textContent}`);
}

carregarPeriodo();
setInterval(carregarPeriodo, 5000);

// dia: so os ultimos 7 dias existem (a base de dados apaga o resto)
const diaData = document.getElementById("dia_data");
const doisDigitos = n => String(n).padStart(2, "0");
const dataLocal = d => `${d.getFullYear()}-${doisDigitos(d.getMonth() + 1)}-${doisDigitos(d.getDate())}`;

const hoje = new Date();
const maisAntigo = new Date();
maisAntigo.setDate(hoje.getDate() - 6);
diaData.max = dataLocal(hoje);
diaData.min = dataLocal(maisAntigo);
diaData.value = dataLocal(hoje);

// meia-noite local ate meia-noite local, em UTC como o servidor guarda
function limitesDia(valor) {
  const [a, m, d] = valor.split("-").map(Number);
  const de = new Date(a, m - 1, d).toISOString();
  const ate = new Date(a, m - 1, d + 1).toISOString();
  return `de=${encodeURIComponent(de)}&ate=${encodeURIComponent(ate)}`;
}

function carregarDia() {
  if (!diaData.value) return;

  const limites = limitesDia(diaData.value);
  preencherEstatisticas(`/estatisticas?${limites}`, "dia", document.getElementById("dia_n"), "neste dia");
  carregar(`/medias?n=96&passo=15&${limites}`, "minuto", GRAFICOS_DIA);
}

function mudarDia(delta) {
  if (!diaData.value) return;

  const [a, m, d] = diaData.value.split("-").map(Number);
  const novo = dataLocal(new Date(a, m - 1, d + delta));
  // comparar texto YYYY-MM-DD funciona porque a ordem alfabetica e a das datas
  if (novo < diaData.min || novo > diaData.max) return;

  diaData.value = novo;
  carregarDia();
}

diaData.addEventListener("change", carregarDia);
document.getElementById("dia_anterior").addEventListener("click", () => mudarDia(-1));
document.getElementById("dia_seguinte").addEventListener("click", () => mudarDia(1));

carregarDia();
setInterval(carregarDia, 60000);
