"""AniCare teste 1: mapa com pins de animais abandonados."""


def create_app(verificar_bd: bool = True):
    """Cria a aplicação Flask.

    Os imports estão dentro da função para que os testes unitários possam importar
    o pacote sem precisarem do .env nem da base de dados.
    """
    from flask import Flask

    from anicare import database
    from anicare.web import registar

    if verificar_bd:
        database.verificar_ligacao()

    app = Flask(__name__)
    registar(app)
    return app
