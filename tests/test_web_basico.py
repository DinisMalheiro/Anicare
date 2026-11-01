"""Testes das páginas principais (precisam do .env e da base de dados)."""

import pytest


@pytest.fixture
def cliente():
    from anicare import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_pagina_inicial(cliente):
    assert cliente.get("/").status_code == 200


def test_pins_em_geojson(cliente):
    resposta = cliente.get("/api/pins")
    assert resposta.status_code == 200
    assert resposta.get_json()["type"] == "FeatureCollection"


def test_publicacao_inexistente_da_404(cliente):
    assert cliente.get("/publicacoes/999999999").status_code == 404


def test_nova_publicacao_exige_login(cliente):
    resposta = cliente.get("/publicacoes/nova")
    assert resposta.status_code == 302
    assert "/auth/login" in resposta.headers["Location"]
