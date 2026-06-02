#!/usr/bin/env python3
"""
Transcritor de audio local com faster-whisper.
Transcreve qualquer audio (incluindo .opus e .ogg do WhatsApp) para texto
fiel em portugues, rodando 100% na maquina, sem chave de API.

Uso:
    python transcrever.py "C:\\caminho\\audio.opus"
    python transcrever.py "audio.opus" --modelo medium
    python transcrever.py "audio.mp3" --idioma en
"""
import argparse
import datetime
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def checar_ffmpeg():
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "ffmpeg nao encontrado no PATH.\n"
            "Instale com: winget install Gyan.FFmpeg\n"
            "Depois feche e reabra o terminal e rode de novo."
        )


def converter_para_wav(origem: Path) -> Path:
    """Normaliza qualquer audio para wav 16kHz mono, formato ideal do Whisper.
    Resolve os containers estranhos que o WhatsApp as vezes entrega."""
    destino = Path(tempfile.gettempdir()) / (origem.stem + "_16k.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(origem), "-ar", "16000", "-ac", "1", str(destino)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return destino


def escolher_dispositivo():
    """Usa GPU NVIDIA se existir, senao cai para CPU automaticamente."""
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


def transcrever(caminho: Path, modelo_nome: str, idioma: str):
    from faster_whisper import WhisperModel

    device, compute_type = escolher_dispositivo()
    print(f"Dispositivo: {device} | modelo: {modelo_nome} | compute: {compute_type}")

    modelo = WhisperModel(modelo_nome, device=device, compute_type=compute_type)
    segmentos, info = modelo.transcribe(
        str(caminho),
        language=idioma,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    # Junta os segmentos em texto corrido, abrindo paragrafo novo
    # quando ha uma pausa longa na fala. Nada e cortado nem resumido.
    partes = []
    paragrafo = []
    ultimo_fim = 0.0
    for seg in segmentos:
        if seg.start - ultimo_fim > 1.5 and paragrafo:
            partes.append(" ".join(paragrafo))
            paragrafo = []
        paragrafo.append(seg.text.strip())
        ultimo_fim = seg.end
    if paragrafo:
        partes.append(" ".join(paragrafo))

    texto = "\n\n".join(partes).strip()
    return texto, info


def salvar(audio_path: Path, texto: str, info, modelo_nome: str) -> Path:
    duracao = str(datetime.timedelta(seconds=round(info.duration)))
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    saida = audio_path.with_suffix(".md")
    cabecalho = (
        f"# Transcricao: {audio_path.name}\n\n"
        f"Data: {agora}  \n"
        f"Duracao: {duracao}  \n"
        f"Modelo: {modelo_nome}  \n\n"
        f"---\n\n"
    )
    saida.write_text(cabecalho + texto + "\n", encoding="utf-8")
    return saida


def main():
    parser = argparse.ArgumentParser(
        description="Transcreve audio para texto fiel em portugues, local."
    )
    parser.add_argument("audio", help="Caminho do arquivo de audio")
    parser.add_argument(
        "--modelo",
        default="large-v3",
        help="Modelo Whisper: large-v3 (melhor), medium ou small (mais rapidos)",
    )
    parser.add_argument("--idioma", default="pt", help="Idioma do audio (padrao: pt)")
    args = parser.parse_args()

    audio_path = Path(args.audio).expanduser().resolve()
    if not audio_path.exists():
        sys.exit(f"Arquivo nao encontrado: {audio_path}")

    checar_ffmpeg()

    print("Convertendo audio...")
    wav = converter_para_wav(audio_path)

    print("Transcrevendo. Na primeira vez o modelo e baixado, pode demorar...")
    texto, info = transcrever(wav, args.modelo, args.idioma)

    saida = salvar(audio_path, texto, info, args.modelo)

    try:
        wav.unlink()
    except OSError:
        pass

    print(f"Pronto: {saida}")


if __name__ == "__main__":
    main()
