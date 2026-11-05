from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

from anicare.database import sessao
from anicare.erros import ErroNegocio
from anicare.repositories.utilizador_repository import UtilizadorRepository
from anicare.services.auth_service import AuthService

bp = Blueprint("auth", __name__, url_prefix="/auth")

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sessão para continuar."
login_manager.login_message_category = "aviso"
# Proteção "basic" (por defeito): se o IP mudar (Wi-Fi <-> dados móveis), a sessão deixa de
# ser "fresca" mas o utilizador não é desligado. A proteção "strong" desligava-o.


class UtilizadorSessao(UserMixin):
    """Adapta o Utilizador do domínio ao que o Flask-Login precisa."""

    def __init__(self, utilizador):
        self.id = utilizador.id
        self.username = utilizador.username
        self.e_admin = utilizador.e_admin
        self._ativo = utilizador.ativo

    @property
    def is_active(self):
        return self._ativo


@login_manager.user_loader
def carregar_utilizador(user_id: str):
    try:
        utilizador_id = int(user_id)
    except ValueError:
        return None
    with sessao() as s:
        utilizador = UtilizadorRepository(s).obter_por_id(utilizador_id)
    return UtilizadorSessao(utilizador) if utilizador and utilizador.ativo else None


def _destino_seguro(destino: str | None) -> str:
    """Só aceita destinos dentro do site (evita redirecionamentos para sites externos)."""
    if destino and destino.startswith("/") and not destino.startswith("//") and "\\" not in destino:
        return destino
    return url_for("mapa.inicio")


@bp.route("/registo", methods=["GET", "POST"])
def registo():
    if request.method == "POST":
        form = request.form
        try:
            if form.get("password") != form.get("password2"):
                raise ErroNegocio("As palavras-passe não coincidem.")
            with sessao() as s:
                AuthService.com_sessao(s).registar(
                    form.get("username"), form.get("email"), form.get("password")
                )
        except ErroNegocio as erro:
            flash(str(erro), "erro")
            return render_template("auth/registo.html", form=form), 400
        flash("Conta criada. Já podes entrar.", "ok")
        return redirect(url_for("auth.login"))
    return render_template("auth/registo.html", form={})


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        with sessao() as s:
            utilizador = AuthService.com_sessao(s).autenticar(
                request.form.get("valor"), request.form.get("password"), request.remote_addr
            )
        if utilizador is None:
            flash("Credenciais inválidas.", "erro")
            return render_template("auth/login.html", destino=request.form.get("next")), 401
        login_user(UtilizadorSessao(utilizador))
        return redirect(_destino_seguro(request.form.get("next")))
    return render_template("auth/login.html", destino=request.args.get("next"))


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão terminada.", "ok")
    return redirect(url_for("mapa.inicio"))
