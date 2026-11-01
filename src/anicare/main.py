"""Ponto de entrada da aplicação.

Desenvolvimento:   python -m anicare.main
                   (ou)  flask --app anicare.main run --debug
Produção:          gunicorn "anicare:create_app()"
"""

from anicare import config, create_app

app = create_app()


def main() -> None:
    app.run(debug=config.DEBUG)


if __name__ == "__main__":
    main()
