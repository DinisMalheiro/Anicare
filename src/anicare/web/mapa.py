from flask import Blueprint, jsonify, render_template, request, send_from_directory

from anicare import config
from anicare.database import sessao
from anicare.erros import ErroNegocio
from anicare.services.publicacao_service import PublicacaoService

bp = Blueprint("mapa", __name__)

ESTADOS = [("avistado", "Avistado"), ("resgatado", "Resgatado"), ("adotado", "Adotado")]


@bp.get("/")
def inicio():
    with sessao() as s:
        especies = PublicacaoService.com_sessao(s).listar_especies()
    return render_template("mapa.html", especies=especies, estados=ESTADOS)


@bp.get("/api/pins")
def pins():
    """Pins do mapa em GeoJSON (um por animal). Filtros: ?especie_id=1&estado=avistado"""
    try:
        with sessao() as s:
            dados = PublicacaoService.com_sessao(s).pins_geojson(
                request.args.get("especie_id", type=int), request.args.get("estado") or None,
                request.args.get("q") or None,
                max(1, request.args.get("pagina", default=1, type=int)),
            )
    except ErroNegocio as erro:
        return jsonify(erro=str(erro)), 400
    return jsonify(dados)


@bp.get("/api/animais-proximos")
def animais_proximos():
    """Animais já registados perto de um ponto: ?lat=38.7&lon=-9.1&especie_id=1&raio=1000"""
    latitude = request.args.get("lat", type=float)
    longitude = request.args.get("lon", type=float)
    if latitude is None or longitude is None:
        return jsonify(erro="Indica lat e lon."), 400
    raio = max(50, min(request.args.get("raio", default=1000, type=int), 5000))
    try:
        with sessao() as s:
            dados = PublicacaoService.com_sessao(s).animais_proximos(
                latitude, longitude, raio, request.args.get("especie_id", type=int)
            )
    except ErroNegocio as erro:
        return jsonify(erro=str(erro)), 400
    return jsonify(dados)


@bp.get("/media/<path:caminho>")
def media(caminho: str):
    """Serve as fotografias enviadas. Em produção, o Caddy/Nginx pode servi-las diretamente."""
    return send_from_directory(config.PASTA_UPLOADS, caminho, max_age=86400)
