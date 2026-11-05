const el = document.getElementById("valores");

async function atualizar() {
    try {
        const r = await fetch("/");
        const d = await r.json();
        el.textContent = r.ok ? `Temperatura: ${d.temperatura} °C | Humidade: ${d.humidade} %` : d.detail;
    } catch (e) {
        el.textContent = "Sem ligacao ao servidor";
    }
}

atualizar();
setInterval(atualizar, 1000);

const button_state_mode = document.getElementById("darkmode");

button_state_mode.addEventListener("click", function () {
  document.body.classList.toggle("dark");
});
