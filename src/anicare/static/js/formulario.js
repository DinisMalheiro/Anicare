// Formulário de novo avistamento: escolher o local no mapa.
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
  let marcador = null;

  function definirLocal(lat, lon, centrar) {
    campoLat.value = lat.toFixed(6);
    campoLon.value = lon.toFixed(6);
    if (marcador) marcador.setLatLng([lat, lon]);
    else marcador = L.marker([lat, lon]).addTo(mapa);
    if (centrar) mapa.setView([lat, lon], 16);
    info.textContent = "Local escolhido: " + lat.toFixed(5) + ", " + lon.toFixed(5);
  }

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
