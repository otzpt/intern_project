const el = document.getElementById("valores");
const avg = document.getElementById("media");

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

atualizar();
setInterval(atualizar, 1000);

const button_state_mode = document.getElementById("darkmode");

button_state_mode.addEventListener("click", function () {
  document.body.classList.toggle("dark");
});
