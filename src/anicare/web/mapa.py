from flask import Blueprint, jsonify, render_template

from anicare.database import sessao
from anicare.services.publicacao_service import PublicacaoService

bp = Blueprint("mapa", __name__)


@bp.get("/")
def inicio():
    return render_template("mapa.html")


@bp.get("/api/pins")
def pins():
    """Pins do mapa em GeoJSON (um por avistamento)."""
    with sessao() as s:
        return jsonify(PublicacaoService.com_sessao(s).pins_geojson())
