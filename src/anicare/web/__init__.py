"""Controladores: recebem os pedidos HTTP, chamam os serviços e devolvem páginas ou JSON."""

from flask import render_template
from flask_wtf.csrf import CSRFError


def _data_pt(data) -> str:
    """Formata uma data/hora na hora local do servidor (dd/mm/aaaa hh:mm)."""
    return data.astimezone().strftime("%d/%m/%Y %H:%M") if data else ""


def _tratador_erro(codigo: int, titulo: str):
    def tratador(_erro):
        return render_template("erro.html", codigo=codigo, titulo=titulo), codigo

    return tratador


def registar(app) -> None:
    """Liga as rotas, os filtros de templates e as páginas de erro."""
    from anicare.web import auth, mapa, publicacoes

    for modulo in (mapa, auth, publicacoes):
        app.register_blueprint(modulo.bp)

    app.add_template_filter(_data_pt, "data_pt")

    for codigo, titulo in (
        (403, "Acesso negado"),
        (404, "Página não encontrada"),
        (500, "Erro interno"),
    ):
        app.register_error_handler(codigo, _tratador_erro(codigo, titulo))
    app.register_error_handler(
        CSRFError, lambda _e: (render_template("erro.html", codigo=400,
                                               titulo="A sessão expirou. Volta atrás e tenta de novo."), 400)
    )
