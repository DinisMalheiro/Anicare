"""Receber, validar, limpar e redimensionar fotografias."""

import io
import uuid
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from anicare.erros import ErroNegocio

FORMATOS_ACEITES = {"JPEG", "PNG", "WEBP"}
LIMITE_BYTES = 10 * 1024 * 1024
LIMITE_PIXEIS = 50_000_000  # protege contra imagens construídas para rebentar a memória
LADO_MAXIMO = 1600
LADO_MINIATURA = 400
QUALIDADE = 80

Image.MAX_IMAGE_PIXELS = LIMITE_PIXEIS


def caminho_miniatura(caminho: str) -> str:
    """fotos/abc.webp  ->  miniaturas/abc.webp (mesmo nome, outra pasta)."""
    if caminho.startswith("fotos/"):
        return "miniaturas/" + caminho[len("fotos/"):]
    return caminho


class ImagemService:
    def __init__(self, pasta_base: Path | None = None):
        if pasta_base is None:
            from anicare import config

            pasta_base = config.PASTA_UPLOADS
        self.pasta_base = Path(pasta_base)

    def guardar(self, ficheiro) -> str:
        """Valida e guarda a imagem. Devolve o caminho relativo (ex.: fotos/ab12.webp).

        - confirma que é mesmo uma imagem (não confia na extensão);
        - corrige a orientação e APAGA os metadados (EXIF), que podem ter o GPS;
        - reduz para no máximo 1600 px e cria uma miniatura de 400 px;
        - converte para WebP e guarda com um nome aleatório.
        """
        dados = ficheiro.read(LIMITE_BYTES + 1)
        if not dados:
            raise ErroNegocio("O ficheiro de imagem está vazio.")
        if len(dados) > LIMITE_BYTES:
            raise ErroNegocio("A imagem excede o limite de 10 MB.")

        mensagem_invalida = (
            "O ficheiro não é uma imagem válida (aceitamos JPEG, PNG e WebP)."
        )
        try:
            with Image.open(io.BytesIO(dados)) as teste:
                if teste.format not in FORMATOS_ACEITES:
                    raise ErroNegocio(mensagem_invalida)
                if teste.width * teste.height > LIMITE_PIXEIS:
                    raise ErroNegocio("A imagem tem dimensões demasiado grandes.")
                teste.verify()
            imagem = Image.open(io.BytesIO(dados))
            imagem = ImageOps.exif_transpose(imagem)
            imagem = self._para_rgb(imagem)
        except ErroNegocio:
            raise
        except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
            raise ErroNegocio(mensagem_invalida) from None

        principal = imagem.copy()
        principal.thumbnail((LADO_MAXIMO, LADO_MAXIMO))
        miniatura = imagem.copy()
        miniatura.thumbnail((LADO_MINIATURA, LADO_MINIATURA))

        nome = f"{uuid.uuid4().hex}.webp"
        for pasta in ("fotos", "miniaturas"):
            (self.pasta_base / pasta).mkdir(parents=True, exist_ok=True)
        principal.save(self.pasta_base / "fotos" / nome, "WEBP", quality=QUALIDADE)
        miniatura.save(self.pasta_base / "miniaturas" / nome, "WEBP", quality=QUALIDADE)
        return f"fotos/{nome}"

    def apagar(self, caminho: str) -> None:
        """Apaga a imagem e a miniatura (usado quando a gravação na BD falha)."""
        base = self.pasta_base.resolve()
        for relativo in (caminho, caminho_miniatura(caminho)):
            ficheiro = (self.pasta_base / relativo).resolve()
            if base in ficheiro.parents:
                ficheiro.unlink(missing_ok=True)

    @staticmethod
    def _para_rgb(imagem: Image.Image) -> Image.Image:
        tem_transparencia = imagem.mode in ("RGBA", "LA") or (
            imagem.mode == "P" and "transparency" in imagem.info
        )
        if tem_transparencia:
            rgba = imagem.convert("RGBA")
            fundo = Image.new("RGB", rgba.size, (255, 255, 255))
            fundo.paste(rgba, mask=rgba.getchannel("A"))
            return fundo
        return imagem.convert("RGB")
