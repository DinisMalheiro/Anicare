from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from anicare.database import sessao
from anicare.erros import ErroNegocio
from anicare.services.comentario_service import ComentarioService
from anicare.services.publicacao_service import PublicacaoService
from anicare.services.voto_service import VotoService
from anicare.repositories.voto_repository import VotoRepository

bp = Blueprint("publicacoes", __name__, url_prefix="/publicacoes")

PORTES = [("pequeno", "Pequeno"), ("medio", "Médio"), ("grande", "Grande")]
SEXOS = [("desconhecido", "Não sei"), ("macho", "Macho"), ("femea", "Fêmea")]


def _converter(valor, tipo, mensagem: str):
    try:
        return tipo(valor)
    except (TypeError, ValueError):
        raise ErroNegocio(mensagem) from None


def _opcional_int(valor, mensagem: str):
    valor = (valor or "").strip()
    return _converter(valor, int, mensagem) if valor else None


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
        comentarios = ComentarioService.com_sessao(s).listar(publicacao_id) if publicacao else []
    if publicacao is None:
        abort(404)
    return render_template("publicacoes/detalhe.html", p=publicacao, comentarios=comentarios)


@bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():
    if request.method == "GET":
        return _formulario({})

    form = request.form
    try:
        dados = {
            "animal_id": _opcional_int(form.get("animal_id"), "Animal inválido."),
            "especie_id": _opcional_int(form.get("especie_id"), "Espécie inválida."),
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
                current_user.id, dados, request.files.get("fotografia")
            )
    except ErroNegocio as erro:
        flash(str(erro), "erro")
        return _formulario(form, 400)

    flash("Pin adicionado.", "ok")
    return redirect(url_for("publicacoes.detalhe", publicacao_id=publicacao_id))


@bp.post("/<int:publicacao_id>/comentarios")
@login_required
def comentar(publicacao_id: int):
    try:
        with sessao() as s:
            ComentarioService.com_sessao(s).comentar(
                publicacao_id, current_user.id, request.form.get("texto"),
                request.files.get("fotografia"),
                _opcional_int(request.form.get("parent_id"), "Comentário inválido."),
            )
        flash("Comentário publicado.", "ok")
    except ErroNegocio as erro:
        flash(str(erro), "erro")
    return redirect(url_for("publicacoes.detalhe", publicacao_id=publicacao_id) + "#comentarios")


@bp.route("/<int:publicacao_id>/editar", methods=["GET", "POST"])
@login_required
def editar(publicacao_id: int):
    with sessao() as s:
        service = PublicacaoService.com_sessao(s)
        atual = service.obter_detalhe(publicacao_id)
        if atual is None:
            abort(404)
        if atual["utilizador_id"] != current_user.id:
            abort(403)
        if request.method == "POST":
            try:
                dados = {
                    "titulo": request.form.get("titulo"),
                    "descricao": request.form.get("descricao"),
                    "animal_id": atual["animal_id"],
                    "especie_id": _opcional_int(request.form.get("especie_id"), "Espécie inválida."),
                    "cor": request.form.get("cor"),
                    "porte": request.form.get("porte"),
                    "sexo": request.form.get("sexo"),
                    "nome": request.form.get("nome"),
                    "idade_aproximada": request.form.get("idade_aproximada"),
                    "estado_saude": request.form.get("estado_saude"),
                    "latitude": atual["latitude"],
                    "longitude": atual["longitude"],
                    "data_avistamento": _converter(
                        request.form.get("data_avistamento"), datetime.fromisoformat, "Data inválida."
                    ),
                }
                service.atualizar(
                    publicacao_id, current_user.id, dados, request.files.get("fotografia")
                )
            except ErroNegocio as erro:
                flash(str(erro), "erro")
            else:
                flash("Publicação atualizada.", "ok")
                return redirect(url_for("publicacoes.detalhe", publicacao_id=publicacao_id))
    return render_template("publicacoes/editar.html", p=atual)


@bp.post("/<int:publicacao_id>/voto")
@login_required
def votar(publicacao_id: int):
    try:
        valor = int(request.form.get("valor", "0"))
        with sessao() as s:
            VotoService(VotoRepository(s)).votar_publicacao(current_user.id, publicacao_id, valor)
    except (ValueError, ErroNegocio) as erro:
        flash(str(erro), "erro")
    return redirect(request.referrer or url_for("publicacoes.detalhe", publicacao_id=publicacao_id))


@bp.post("/<int:publicacao_id>/apagar")
@login_required
def apagar(publicacao_id: int):
    if not current_user.e_admin:
        abort(403)
    with sessao() as s:
        if not PublicacaoService.com_sessao(s).publicacoes.apagar(publicacao_id):
            abort(404)
    flash("Publicação removida.", "ok")
    return redirect(url_for("mapa.inicio"))


@bp.post("/<int:publicacao_id>/estado")
@login_required
def estado(publicacao_id: int):
    with sessao() as s:
        service = PublicacaoService.com_sessao(s)
        detalhe = service.obter_detalhe(publicacao_id)
        if detalhe is None:
            abort(404)
        if detalhe["utilizador_id"] != current_user.id and not current_user.e_admin:
            abort(403)
        service.atualizar_estado(detalhe["animal_id"], request.form.get("estado"))
    flash("Estado do animal atualizado.", "ok")
    return redirect(url_for("publicacoes.detalhe", publicacao_id=publicacao_id))


@bp.post("/comentarios/<int:comentario_id>/apagar")
@login_required
def apagar_comentario(comentario_id: int):
    if not current_user.e_admin:
        abort(403)
    with sessao() as s:
        ComentarioService.com_sessao(s).apagar(comentario_id)
    flash("Comentário removido.", "ok")
    return redirect(request.referrer or url_for("mapa.inicio"))


@bp.post("/<int:publicacao_id>/comentarios/<int:comentario_id>/responder")
@login_required
def responder(publicacao_id: int, comentario_id: int):
    try:
        with sessao() as s:
            ComentarioService.com_sessao(s).comentar(
                publicacao_id, current_user.id, request.form.get("texto"),
                request.files.get("fotografia"), comentario_id,
            )
        flash("Resposta publicada.", "ok")
    except ErroNegocio as erro:
        flash(str(erro), "erro")
    return redirect(url_for("publicacoes.detalhe", publicacao_id=publicacao_id) + "#comentarios")


@bp.post("/comentarios/<int:comentario_id>/voto")
@login_required
def votar_comentario(comentario_id: int):
    try:
        valor = int(request.form.get("valor", "0"))
        with sessao() as s:
            VotoService(VotoRepository(s)).votar_comentario(
                current_user.id, comentario_id, valor
            )
    except (ValueError, ErroNegocio) as erro:
        flash(str(erro), "erro")
    return redirect(request.referrer or url_for("mapa.inicio"))
