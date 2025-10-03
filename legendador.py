from __future__ import annotations

from pathlib import Path
import tempfile
from typing import IO, Union

from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment

ArquivoTipo = Union[str, Path, IO[bytes]]

DEFAULT_CORRECOES: dict[str, str] = {
    "seticismo": "ceticismo",
}


def _persistir_arquivo_temporario(arquivo: ArquivoTipo, destino: Path) -> tuple[Path, str, str]:
    """Recebe um caminho ou file-like e devolve (path_em_disco, extensao, nome_base)."""

    if isinstance(arquivo, (str, Path)):
        origem = Path(arquivo)
        if not origem.exists():
            raise FileNotFoundError(f"Arquivo nao encontrado: {origem}")
        ext = origem.suffix.lstrip('.') or 'mp3'
        return origem, ext, origem.stem

    nome_origem = getattr(arquivo, 'name', 'arquivo.mp3')
    ext = Path(nome_origem).suffix.lstrip('.') or 'mp3'
    destino_final = destino.with_suffix(f'.{ext}')

    conteudo = arquivo.read()
    if isinstance(conteudo, str):
        conteudo = conteudo.encode()
    destino_final.write_bytes(conteudo)

    if hasattr(arquivo, 'seek'):
        try:
            arquivo.seek(0)
        except Exception:
            pass

    nome_base = Path(nome_origem).stem or 'legenda'
    return destino_final, ext, nome_base


def _aplicar_correcoes(texto: str, correcoes: dict[str, str]) -> str:
    """Aplica substituicoes simples palavra->palavra na legenda final."""

    resultado = texto
    for original, substituto in correcoes.items():
        resultado = resultado.replace(original, substituto)
    return resultado


def legendar(
    arquivo_selecionado: ArquivoTipo = 'oswaldo_porchat.mp4',
    contexto: str | None = None,
    correcoes: dict[str, str] | None = None,
) -> str:
    """Converte video/arquivo de audio em MP3, chama Whisper e grava a legenda SRT."""

    load_dotenv()
    cliente = OpenAI()

    with tempfile.TemporaryDirectory() as pasta_temp:
        caminho_temp = Path(pasta_temp) / 'entrada'
        caminho_entrada, extensao_origem, nome_base = _persistir_arquivo_temporario(
            arquivo_selecionado, caminho_temp
        )

        audio = AudioSegment.from_file(file=str(caminho_entrada), format=extensao_origem)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)

        caminho_audio = Path(pasta_temp) / 'audio.mp3'
        audio.export(str(caminho_audio), format='mp3', bitrate='64k')

        parametros_extra = {}
        if contexto:
            parametros_extra['prompt'] = contexto

        with open(caminho_audio, 'rb') as arquivo_audio:
            transcricao = cliente.audio.transcriptions.create(
                file=arquivo_audio,
                model='whisper-1',
                language='pt',
                response_format='srt',
                **parametros_extra,
            )

    legenda = transcricao.text if hasattr(transcricao, 'text') else str(transcricao)

    mapa_correcoes = DEFAULT_CORRECOES.copy()
    if correcoes:
        mapa_correcoes.update(correcoes)
    legenda = _aplicar_correcoes(legenda, mapa_correcoes)

    caminho_saida = Path(f"{nome_base}_legenda.srt")
    with open(caminho_saida, 'w', encoding='utf-8') as arquivo_legenda:
        arquivo_legenda.write(legenda)

    return legenda


if __name__ == '__main__':
    legendar()
    print('Legenda gerada em arquivo *_legenda.srt.')