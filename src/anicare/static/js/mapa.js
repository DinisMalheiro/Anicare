// Mapa principal: mostra um pin por animal (último avistamento) e respeita os filtros.
(function () {
  "use strict";

  const mapa = L.map("mapa").setView([39.5, -8.0], 6); // centro de Portugal
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; contribuidores do OpenStreetMap",
  }).addTo(mapa);

  const camada = L.layerGroup().addTo(mapa);
  const formulario = document.getElementById("filtros");
  const contagem = document.getElementById("contagem");
  let primeiraVez = true;

  // O popup é construído com textContent (nunca innerHTML): os títulos vêm dos utilizadores.
  function criarPopup(p) {
    const caixa = document.createElement("div");
    caixa.className = "popup-pin";

    if (p.foto) {
      const img = document.createElement("img");
      img.src = "/media/" + p.foto;
      img.alt = "Fotografia do animal";
      caixa.appendChild(img);
    }
    const titulo = document.createElement("strong");
    titulo.textContent = p.titulo;
    caixa.appendChild(titulo);

    const linhas = [
      [p.especie, p.cor, p.porte].filter(Boolean).join(" · "),
      "Estado: " + p.estado,
      "Visto em " + new Date(p.data).toLocaleString("pt-PT"),
    ];
    for (const texto of linhas) {
      const par = document.createElement("p");
      par.textContent = texto;
      caixa.appendChild(par);
    }
    const ligacao = document.createElement("a");
    ligacao.href = "/publicacoes/" + p.id;
    ligacao.textContent = "Ver publicação";
    caixa.appendChild(ligacao);
    return caixa;
  }

  async function carregar() {
    const params = new URLSearchParams(new FormData(formulario));
    for (const [chave, valor] of Array.from(params)) {
      if (!valor) params.delete(chave);
    }
    const resposta = await fetch("/api/pins?" + params.toString());
    if (!resposta.ok) {
      contagem.textContent = "Não foi possível carregar os animais.";
      return;
    }
    const dados = await resposta.json();
    camada.clearLayers();
    const geojson = L.geoJSON(dados, {
      onEachFeature: (feature, marcador) =>
        marcador.bindPopup(criarPopup(feature.properties)),
    }).addTo(camada);

    const n = dados.features.length;
    contagem.textContent = n === 1 ? "1 animal" : n + " animais";
    if (primeiraVez && n > 0) {
      mapa.fitBounds(geojson.getBounds(), { maxZoom: 14, padding: [30, 30] });
    }
    primeiraVez = false;
  }

  formulario.addEventListener("change", carregar);
  carregar();
})();
