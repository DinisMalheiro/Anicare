from html import escape
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for, Response
from flask_login import current_user, login_required
from anicare.database import sessao
from anicare.repositories.perfil_repository import PerfilRepository
from anicare.services.imagem_service import ImagemService
from anicare.erros import ErroNegocio

bp = Blueprint("perfis", __name__, url_prefix="/perfis")


@bp.get("/<username>")
def ver(username):
    with sessao() as s:
        perfil = PerfilRepository(s).obter(username)
    if perfil is None:
        abort(404)
    return render_template("perfis/ver.html", perfil=perfil)


@bp.get("/<username>/avatar")
def avatar(username):
    with sessao() as s:
        perfil = PerfilRepository(s).obter(username)
    if perfil is None:
        abort(404)
    if perfil["avatar_caminho"]:
        from anicare import config
        from flask import send_from_directory
        return send_from_directory(config.PASTA_UPLOADS, perfil["avatar_caminho"])
    nome = escape((perfil["nome_exibicao"] or perfil["username"])[:1].upper())
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#1f4e79"/><text x="50" y="62" text-anchor="middle" font-size="52" fill="white">{nome}</text></svg>'
    return Response(svg, mimetype="image/svg+xml")


@bp.route("/editar", methods=["GET", "POST"])
@login_required
def editar():
    with sessao() as s:
        repositorio = PerfilRepository(s)
        perfil = repositorio.obter(current_user.username)
        if request.method == "POST":
            nome = (request.form.get("nome_exibicao") or "").strip() or None
            bio = (request.form.get("bio") or "").strip() or None
            if (nome and len(nome) > 60) or (bio and len(bio) > 500):
                flash("O nome ou a biografia excede o limite permitido.", "erro")
            else:
                fotografia = request.files.get("avatar")
                caminho = None
                try:
                    if fotografia is not None and fotografia.filename:
                        caminho = ImagemService().guardar(fotografia)
                    antigo = repositorio.guardar(current_user.id, nome, bio, caminho)
                except ErroNegocio as erro:
                    if caminho:
                        ImagemService().apagar(caminho)
                    flash(str(erro), "erro")
                else:
                    if caminho and antigo:
                        ImagemService().apagar(antigo)
                    current_user.nome_exibicao = nome
                    flash("Perfil atualizado.", "ok")
                    return redirect(url_for("perfis.ver", username=current_user.username))
    return render_template("perfis/editar.html", perfil=perfil or {})
