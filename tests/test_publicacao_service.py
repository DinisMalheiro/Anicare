"""Testes do serviço com repositórios falsos (sem base de dados)."""

from datetime import datetime, timedelta

import pytest

from anicare.erros import ErroNegocio
from anicare.services.publicacao_service import PublicacaoService


class PublicacoesFalso:
    def __init__(self, falhar=False):
        self.criadas, self.falhar = [], falhar

    def criar(self, publicacao):
        if self.falhar:
            raise RuntimeError("a base de dados falhou")
        self.criadas.append(publicacao)
        return 10


class AnimaisFalso:
    def __init__(self, existentes=()):
        self.existentes, self.criados = set(existentes), []

    def obter_por_id(self, animal_id):
        return {"id": animal_id} if animal_id in self.existentes else None

    def criar(self, animal):
        self.criados.append(animal)
        return 5


def _dados(**alteracoes):
    dados = dict(
        especie_id=1, cor="castanho", porte="medio", sexo="macho",
        titulo="Cão perdido", descricao="", latitude=38.7, longitude=-9.1,
        data_avistamento=datetime.now() - timedelta(hours=1),
    )
    dados.update(alteracoes)
    return dados


def _servico(publicacoes=None, animais=None):
    publicacoes = publicacoes or PublicacoesFalso()
    animais = animais or AnimaisFalso()
    return PublicacaoService(publicacoes, animais), publicacoes, animais


def test_animal_novo_cria_animal_e_publicacao_ligados():
    servico, publicacoes, animais = _servico()
    assert servico.criar_avistamento(1, _dados()) == 10
    assert len(animais.criados) == 1
    assert publicacoes.criadas[0].animal_id == 5


def test_dados_invalidos_nao_tocam_na_bd():
    servico, publicacoes, animais = _servico()
    with pytest.raises(ErroNegocio):
        servico.criar_avistamento(1, _dados(latitude=200))
    assert publicacoes.criadas == [] and animais.criados == []
