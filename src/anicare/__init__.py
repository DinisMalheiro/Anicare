"""AniCare: mapa colaborativo de animais abandonados."""


def create_app(verificar_bd: bool = True):
    """Cria a aplicação Flask e liga todas as peças.

    Ordem do arranque:
      1. lê a configuração (.env);
      2. confirma que a base de dados responde (PostgreSQL + PostGIS);
      3. configura segurança (cookies, CSRF, login, proxy);
      4. regista as rotas (web/), os filtros de templates e o bloqueio de IPs.

    Os imports estão dentro da função para que importar o pacote (por exemplo
    nos testes unitários) não exija o .env nem a base de dados.
    """
    from flask import Flask
    from flask_wtf.csrf import CSRFProtect
    from werkzeug.middleware.proxy_fix import ProxyFix

    from anicare import config, database
    from anicare.web import auth, registar

    if verificar_bd:
        database.verificar_ligacao()

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.SECRET_KEY,
        MAX_CONTENT_LENGTH=config.TAMANHO_MAXIMO_UPLOAD,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=config.COOKIES_SEGUROS,
    )
    if config.CONFIAR_PROXY:
        # Atrás do Caddy/Nginx: usa o IP real do visitante (X-Forwarded-For).
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    CSRFProtect(app)
    auth.login_manager.init_app(app)
    registar(app)
    return app
