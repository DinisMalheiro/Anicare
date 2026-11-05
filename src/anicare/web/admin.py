from datetime import datetime
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from anicare.database import sessao
from anicare.repositories.bloqueio_repository import BloqueioRepository
from anicare.domain.bloqueio import Bloqueio

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _admin():
    if not current_user.is_authenticated or not current_user.e_admin:
        abort(403)


@bp.get("/")
@login_required
def inicio():
    _admin()
    return render_template("admin/inicio.html")


@bp.post("/bloqueios")
@login_required
def bloquear():
    _admin()
    try:
        expira = request.form.get("expira_em") or None
        bloqueio = Bloqueio(
            criado_por=current_user.id,
            utilizador_id=int(request.form["utilizador_id"]) if request.form.get("utilizador_id") else None,
            ip=request.form.get("ip") or None,
            ban_motivo=request.form.get("motivo"),
            expira_em=datetime.fromisoformat(expira) if expira else None,
        )
        with sessao() as s:
            BloqueioRepository(s).criar(bloqueio)
    except (ValueError, KeyError) as erro:
        flash(str(erro), "erro")
    else:
        flash("Bloqueio criado.", "ok")
    return redirect(url_for("admin.inicio"))
