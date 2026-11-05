from anicare.domain.comentario import Comentario
from anicare.domain.fotografia import Fotografia
from anicare.erros import ErroDominio, ErroNegocio
from anicare.repositories.comentario_repository import ComentarioRepository
from anicare.repositories.fotografia_repository import FotografiaRepository
from anicare.repositories.publicacao_repository import PublicacaoRepository
from anicare.services.imagem_service import ImagemService


class ComentarioService:
    def __init__(self, comentarios, publicacoes, fotografias, imagens):
        self.comentarios = comentarios
        self.publicacoes = publicacoes
        self.fotografias = fotografias
        self.imagens = imagens

    @classmethod
    def com_sessao(cls, sessao):
        return cls(
            ComentarioRepository(sessao),
            PublicacaoRepository(sessao),
            FotografiaRepository(sessao),
            ImagemService(),
        )

    def listar(self, publicacao_id: int) -> list[dict]:
        comentarios = self.comentarios.listar_por_publicacao(publicacao_id)
        fotos = self.fotografias.listar_por_comentarios([c["id"] for c in comentarios])
        for c in comentarios:
            c["fotos"] = fotos.get(c["id"], [])
        return comentarios

    def comentar(self, publicacao_id: int, utilizador_id: int, texto: str, ficheiro=None) -> int:
        if not self.publicacoes.existe(publicacao_id):
            raise ErroNegocio("A publicação não existe.")
        try:
            comentario = Comentario(
                publicacao_id=publicacao_id, utilizador_id=utilizador_id, texto=texto
            )
        except ErroDominio as erro:
            raise ErroNegocio(str(erro)) from None

        caminho = None
        if ficheiro is not None and getattr(ficheiro, "filename", ""):
            caminho = self.imagens.guardar(ficheiro)
        try:
            comentario_id = self.comentarios.criar(comentario)
            if caminho:
                self.fotografias.criar(Fotografia(caminho=caminho, comentario_id=comentario_id))
        except Exception:
            if caminho:
                self.imagens.apagar(caminho)
            raise
        return comentario_id
