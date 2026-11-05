// Formulário de novo avistamento: escolher o local no mapa e evitar animais duplicados.
(function () {
  "use strict";

  const mapa = L.map("mapa-escolha").setView([39.5, -8.0], 6);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; contribuidores do OpenStreetMap",
  }).addTo(mapa);

  const campoLat = document.getElementById("latitude");
  const campoLon = document.getElementById("longitude");
  const info = document.getElementById("coordenadas");
  const especie = document.getElementById("especie_id");
  const proximos = document.getElementById("proximos");
  const dadosAnimal = document.getElementById("dados-animal");
  let marcador = null;

  function definirLocal(lat, lon, centrar) {
    campoLat.value = lat.toFixed(6);
    campoLon.value = lon.toFixed(6);
    if (marcador) marcador.setLatLng([lat, lon]);
    else marcador = L.marker([lat, lon]).addTo(mapa);
    if (centrar) mapa.setView([lat, lon], 16);
    info.textContent = "Local escolhido: " + lat.toFixed(5) + ", " + lon.toFixed(5);
    procurarProximos();
  }

  // Pergunta à API se já existem animais parecidos perto deste local.
  async function procurarProximos() {
    proximos.replaceChildren();
    dadosAnimal.disabled = false;
    if (!campoLat.value || !campoLon.value) return;

    const params = new URLSearchParams({ lat: campoLat.value, lon: campoLon.value });
    if (especie.value) params.set("especie_id", especie.value);
    const resposta = await fetch("/api/animais-proximos?" + params.toString());
    if (!resposta.ok) return;
    const animais = await resposta.json();
    if (animais.length === 0) return;

    const pergunta = document.createElement("h2");
    pergunta.textContent = "Já existem animais perto deste local. É algum deles?";
    proximos.appendChild(pergunta);

    for (const a of animais) {
      const etiqueta = document.createElement("label");
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "animal_id";
      radio.value = a.animal_id;
      etiqueta.appendChild(radio);
      if (a.foto) {
        const img = document.createElement("img");
        img.src = "/media/" + a.foto;
        img.alt = "";
        etiqueta.appendChild(img);
      }
      const texto = document.createElement("span");
      texto.textContent =
        a.especie + ", " + a.cor + ", " + a.porte + " (a " + a.distancia_m + " m): " + a.titulo;
      etiqueta.appendChild(texto);
      proximos.appendChild(etiqueta);
    }

    const novo = document.createElement("label");
    const radioNovo = document.createElement("input");
    radioNovo.type = "radio";
    radioNovo.name = "animal_id";
    radioNovo.value = "";
    radioNovo.checked = true;
    novo.appendChild(radioNovo);
    const textoNovo = document.createElement("span");
    textoNovo.textContent = "Não, é um animal novo";
    novo.appendChild(textoNovo);
    proximos.appendChild(novo);
  }

  // Se escolher um animal existente, os campos do animal deixam de ser necessários.
  proximos.addEventListener("change", (evento) => {
    if (evento.target.name === "animal_id") {
      dadosAnimal.disabled = evento.target.value !== "";
    }
  });

  especie.addEventListener("change", procurarProximos);
  mapa.on("click", (evento) => definirLocal(evento.latlng.lat, evento.latlng.lng, false));

  document.getElementById("usar-localizacao").addEventListener("click", () => {
    if (!navigator.geolocation) {
      info.textContent = "O teu navegador não suporta localização.";
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => definirLocal(pos.coords.latitude, pos.coords.longitude, true),
      () => { info.textContent = "Não foi possível obter a tua localização."; }
    );
  });

  // Se o formulário voltou com erros, recupera o local já escolhido.
  if (campoLat.value && campoLon.value) {
    definirLocal(parseFloat(campoLat.value), parseFloat(campoLon.value), true);
  }
})();
