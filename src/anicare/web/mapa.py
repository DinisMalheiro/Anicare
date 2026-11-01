from flask import Blueprint, jsonify, render_template, request

from anicare.database import sessao
from anicare.erros import ErroNegocio
from anicare.services.pin_service import PinService

bp = Blueprint("mapa", __name__)


@bp.get("/")
def inicio():
    return render_template("mapa.html")


@bp.get("/api/pins")
def listar_pins():
    """Todos os pins em GeoJSON."""
    with sessao() as s:
        return jsonify(PinService.com_sessao(s).listar_geojson())


@bp.post("/api/pins")
def criar_pin():
    """Cria um pin. Recebe JSON: titulo, especie, latitude, longitude, descricao."""
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro="Pedido inválido."), 400
    try:
        with sessao() as s:
            pin = PinService.com_sessao(s).criar(dados)
    except ErroNegocio as erro:
        return jsonify(erro=str(erro)), 400
    return jsonify(pin), 201
