"""Controladores: recebem os pedidos HTTP, chamam os serviços e devolvem páginas ou JSON."""

from flask import render_template, request
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from anicare.database import sessao
from anicare.services.bloqueio_service import BloqueioService


def _verificar_bloqueio():
    """Corre antes de cada pedido: recusa contas e IPs bloqueados."""
    if request.endpoint in (None, "static"):
        return None
    utilizador_id = current_user.id if current_user.is_authenticated else None
    with sessao() as s:
        motivo = BloqueioService.com_sessao(s).verificar(request.remote_addr, utilizador_id)
    if motivo:
        return render_template("bloqueado.html", motivo=motivo), 403
    return None


def _data_pt(data) -> str:
    """Formata uma data/hora na hora local do servidor (dd/mm/aaaa hh:mm)."""
    return data.astimezone().strftime("%d/%m/%Y %H:%M") if data else ""


def _tratador_erro(codigo: int, titulo: str):
    def tratador(_erro):
        return render_template("erro.html", codigo=codigo, titulo=titulo), codigo

    return tratador


def registar(app) -> None:
    """Liga as rotas, o bloqueio de IPs, os filtros de templates e as páginas de erro."""
    from anicare.web import admin, auth, mapa, mensagens, perfis, publicacoes

    for modulo in (mapa, auth, publicacoes, perfis, mensagens, admin):
        app.register_blueprint(modulo.bp)

    app.before_request(_verificar_bloqueio)
    app.add_template_filter(_data_pt, "data_pt")

    for codigo, titulo in (
        (403, "Acesso negado"),
        (404, "Página não encontrada"),
        (413, "Ficheiro demasiado grande (máximo 10 MB)"),
        (500, "Erro interno"),
    ):
        app.register_error_handler(codigo, _tratador_erro(codigo, titulo))
    app.register_error_handler(
        CSRFError, lambda _e: (render_template("erro.html", codigo=400,
                                               titulo="A sessão expirou. Volta atrás e tenta de novo."), 400)
    )
