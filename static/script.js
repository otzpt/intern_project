const el = document.getElementById("valores");
const avg = document.getElementById("media_texto");

async function atualizar() {
    try {
      const r = await fetch("/");
      const m = await fetch("/media");
      const d = await r.json();
      const v = await m.json();

      el.textContent = r.ok ? `Temperatura: ${d.temperatura.toFixed(1)} °C | Humidade: ${d.humidade.toFixed(1)} %` : d.detail;
      avg.textContent = m.ok ? `Media temperatura: ${v.temperatura.toFixed(1)} ºC | Media humidade: ${v.humidade.toFixed(1)} %` : v.detail;
    } catch (e) {
      el.textContent = "Sem ligacao ao servidor";
      avg.textContent = "Sem ligacao ao servidor";
    }
}

// o servidor responde com a ultima leitura guardada, por isso 1 s e barato
atualizar();
setInterval(atualizar, 1000);

const button_state_mode = document.getElementById("darkmode");

button_state_mode.addEventListener("click", function () {
  // toggle devolve true quando a classe ficou ligada
  const escuro = document.body.classList.toggle("dark");
  // o texto diz para que modo vai mudar
  button_state_mode.textContent = escuro ? "light" : "dark";
});

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

function horaLocal(hora) {
  const d = new Date(hora.replace(" ", "T") + "Z");
  return d.toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" });
}

function desenhar(id, valores, horas, unidade, alcanceMin) {
  // sem leituras, Math.min() da Infinity
  if (valores.length === 0) return;

  const { min, max } = escalaY(valores, alcanceMin);
  const largura = LARGURA - MARGEM.esquerda - MARGEM.direita;
  const altura = ALTURA - MARGEM.cima - MARGEM.baixo;

  // o "|| 1" evita dividir por 0 com um so valor
  const x = i => MARGEM.esquerda + (i * largura) / ((valores.length - 1) || 1);

  // o y do SVG cresce para baixo
  const y = v => MARGEM.cima + altura - ((v - min) / (max - min)) * altura;

  const svg = document.getElementById(id);
  svg.replaceChildren();

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

// a media por minuto so muda uma vez por minuto
carregar("/medias?n=15", "minuto", GRAFICOS_MEDIA);
setInterval(() => carregar("/medias?n=15", "minuto", GRAFICOS_MEDIA), 60000);
