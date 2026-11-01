"""Testes das páginas (precisam do .env e da base de dados com o schema.sql). Só leem dados."""

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


def test_pin_invalido_da_erro_400(cliente):
    resposta = cliente.post("/api/pins", json={"titulo": "", "especie": "cão", "latitude": 1, "longitude": 1})
    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_pedido_sem_json_da_erro_400(cliente):
    assert cliente.post("/api/pins", data="isto nao e json").status_code == 400
