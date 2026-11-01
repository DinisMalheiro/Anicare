
from anicare import config, create_app

app = create_app()


def main() -> None:
    app.run(debug=config.DEBUG)


if __name__ == "__main__":
    main()
