from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from anicare.database import sessao
from anicare.erros import ErroNegocio
from anicare.services.publicacao_service import PublicacaoService

bp = Blueprint("publicacoes", __name__, url_prefix="/publicacoes")

PORTES = [("pequeno", "Pequeno"), ("medio", "Médio"), ("grande", "Grande")]
SEXOS = [("desconhecido", "Não sei"), ("macho", "Macho"), ("femea", "Fêmea")]


def _converter(valor, tipo, mensagem: str):
    try:
        return tipo(valor)
    except (TypeError, ValueError):
        raise ErroNegocio(mensagem) from None


def _formulario(form, estado: int = 200):
    with sessao() as s:
        especies = PublicacaoService.com_sessao(s).listar_especies()
    agora = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return (
        render_template(
            "publicacoes/formulario.html",
            form=form, especies=especies, portes=PORTES, sexos=SEXOS, agora=agora,
        ),
        estado,
    )


@bp.get("/<int:publicacao_id>")
def detalhe(publicacao_id: int):
    with sessao() as s:
        publicacao = PublicacaoService.com_sessao(s).obter_detalhe(publicacao_id)
    if publicacao is None:
        abort(404)
    return render_template("publicacoes/detalhe.html", p=publicacao)


@bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():
    if request.method == "GET":
        return _formulario({})

    form = request.form
    try:
        dados = {
            "especie_id": _converter(form.get("especie_id"), int, "Escolhe a espécie."),
            "cor": form.get("cor"),
            "porte": form.get("porte"),
            "sexo": form.get("sexo"),
            "nome": form.get("nome"),
            "idade_aproximada": form.get("idade_aproximada"),
            "estado_saude": form.get("estado_saude"),
            "titulo": form.get("titulo"),
            "descricao": form.get("descricao"),
            "latitude": _converter(form.get("latitude"), float, "Escolhe o local no mapa."),
            "longitude": _converter(form.get("longitude"), float, "Escolhe o local no mapa."),
            "data_avistamento": _converter(
                form.get("data_avistamento"), datetime.fromisoformat, "Data inválida."
            ),
        }
        with sessao() as s:
            publicacao_id = PublicacaoService.com_sessao(s).criar_avistamento(
                current_user.id, dados
            )
    except ErroNegocio as erro:
        flash(str(erro), "erro")
        return _formulario(form, 400)

    flash("Avistamento publicado.", "ok")
    return redirect(url_for("publicacoes.detalhe", publicacao_id=publicacao_id))
