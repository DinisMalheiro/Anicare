"""AniCare: mapa colaborativo de animais abandonados."""


def create_app(verificar_bd: bool = True):
    """Cria a aplicação Flask e liga todas as peças.

    Ordem do arranque: configuração (.env) -> confirmar a base de dados ->
    segurança (CSRF, login) -> rotas (web/).

    Os imports estão dentro da função para que importar o pacote (por exemplo
    nos testes unitários) não exija o .env nem a base de dados.
    """
    from flask import Flask
    from flask_wtf.csrf import CSRFProtect

    from anicare import config, database
    from anicare.web import auth, registar

    if verificar_bd:
        database.verificar_ligacao()

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.SECRET_KEY,
    )
    CSRFProtect(app)
    auth.login_manager.init_app(app)
    registar(app)
    return app
