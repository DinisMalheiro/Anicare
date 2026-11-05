from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from anicare.database import sessao
from anicare.repositories.mensagem_repository import MensagemRepository
from anicare.services.mensagem_service import MensagemService
from anicare.erros import ErroNegocio

bp = Blueprint("mensagens", __name__, url_prefix="/mensagens")


@bp.get("/")
@login_required
def caixa():
    with sessao() as s:
        conversas = MensagemRepository(s).conversas(current_user.id)
    return render_template("mensagens/caixa.html", conversas=conversas)


@bp.route("/<int:outro_id>", methods=["GET", "POST"])
@login_required
def conversa(outro_id):
    with sessao() as s:
        repositorio = MensagemRepository(s)
        outro = repositorio.obter_utilizador(outro_id)
        if outro is None or outro_id == current_user.id:
            abort(404)
        if request.method == "POST":
            try:
                MensagemService(repositorio).enviar(
                    current_user.id, outro_id, request.form.get("texto")
                )
            except ErroNegocio as erro:
                flash(str(erro), "erro")
            else:
                return redirect(url_for("mensagens.conversa", outro_id=outro_id))
        repositorio.marcar_conversa_como_lida(current_user.id, outro_id)
        mensagens = repositorio.conversa(current_user.id, outro_id)
    return render_template(
        "mensagens/conversa.html", mensagens=mensagens, outro_id=outro_id,
        outro_nome=outro["nome_exibicao"], outro_username=outro["username"],
    )
