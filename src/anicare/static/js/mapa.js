// Mapa: mostra os pins e deixa criar um novo ao clicar no mapa.
(function () {
  "use strict";

  const mapa = L.map("mapa").setView([39.5, -8.0], 6); // centro de Portugal
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; contribuidores do OpenStreetMap",
  }).addTo(mapa);

  const camada = L.layerGroup().addTo(mapa);
  const contagem = document.getElementById("contagem");
  const formulario = document.getElementById("novo-pin");
  const coordenadas = document.getElementById("coordenadas");
  const caixaErro = document.getElementById("erro");
  let total = 0;
  let marcadorTemporario = null;
  let local = null;

  // O popup é construído com textContent (nunca innerHTML): o texto vem dos utilizadores.
  function criarPopup(p) {
    const caixa = document.createElement("div");
    const titulo = document.createElement("strong");
    titulo.textContent = p.titulo;
    caixa.appendChild(titulo);
    const linhas = [p.especie, p.descricao, new Date(p.data).toLocaleString("pt-PT")];
    for (const texto of linhas.filter(Boolean)) {
      const par = document.createElement("p");
      par.textContent = texto;
      caixa.appendChild(par);
    }
    return caixa;
  }

  function desenhar(feature) {
    return L.geoJSON(feature, {
      onEachFeature: (f, marcador) => marcador.bindPopup(criarPopup(f.properties)),
    }).addTo(camada);
  }

  function mostrarContagem() {
    contagem.textContent = total === 1 ? "1 pin" : total + " pins";
  }

  async function carregar() {
    const resposta = await fetch("/api/pins");
    if (!resposta.ok) {
      contagem.textContent = "Não foi possível carregar os pins.";
      return;
    }
    const dados = await resposta.json();
    const grupo = L.geoJSON(dados, {
      onEachFeature: (f, marcador) => marcador.bindPopup(criarPopup(f.properties)),
    }).addTo(camada);
    total = dados.features.length;
    mostrarContagem();
    if (dados.features.length > 0) {
      mapa.fitBounds(grupo.getBounds(), { maxZoom: 14, padding: [30, 30] });
    }
  }

  function fecharFormulario() {
    formulario.hidden = true;
    formulario.reset();
    caixaErro.hidden = true;
    if (marcadorTemporario) {
      mapa.removeLayer(marcadorTemporario);
      marcadorTemporario = null;
    }
    local = null;
  }

  mapa.on("click", (evento) => {
    local = evento.latlng;
    if (marcadorTemporario) marcadorTemporario.setLatLng(local);
    else marcadorTemporario = L.marker(local, { opacity: 0.6 }).addTo(mapa);
    coordenadas.textContent = "Local: " + local.lat.toFixed(5) + ", " + local.lng.toFixed(5);
    formulario.hidden = false;
    formulario.elements.titulo.focus();
  });

  document.getElementById("cancelar").addEventListener("click", fecharFormulario);

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (!local) return;
    const dados = {
      titulo: formulario.elements.titulo.value,
      especie: formulario.elements.especie.value,
      descricao: formulario.elements.descricao.value,
      latitude: local.lat,
      longitude: local.lng,
    };
    const resposta = await fetch("/api/pins", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });
    const corpo = await resposta.json();
    if (!resposta.ok) {
      caixaErro.textContent = corpo.erro || "Não foi possível guardar o pin.";
      caixaErro.hidden = false;
      return;
    }
    fecharFormulario();
    desenhar(corpo).eachLayer((m) => m.openPopup());
    total += 1;
    mostrarContagem();
  });

  carregar();
})();
