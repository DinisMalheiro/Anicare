"""Controladores: recebem os pedidos HTTP, chamam os serviços e devolvem páginas ou JSON."""

from flask import jsonify, render_template, request


def _erro(codigo: int, titulo: str):
    def tratador(_erro):
        if request.path.startswith("/api/"):
            return jsonify(erro=titulo), codigo
        return render_template("erro.html", codigo=codigo, titulo=titulo), codigo

    return tratador


def registar(app) -> None:
    from anicare.web import mapa

    app.register_blueprint(mapa.bp)
    for codigo, titulo in ((404, "Página não encontrada"), (500, "Erro interno")):
        app.register_error_handler(codigo, _erro(codigo, titulo))
