---
name: transcritor-audio
description: Transcreve arquivos de audio para texto fiel em portugues, rodando o Whisper localmente via faster-whisper, sem chave de API e sem o audio sair da maquina. Use sempre que a pessoa pedir para transcrever um audio, um podcast, um audio longo do WhatsApp, ou mencionar arquivos .opus, .ogg, .mp3, .m4a ou .wav que precisam virar texto. Dispara tambem quando a pessoa fala em passar audio para texto, transcricao, ou quer extrair o conteudo falado de um arquivo de som, mesmo sem usar a palavra transcrever.
author: Ana Retore (https://github.com/anaretore-thecosmo)
license: MIT
---

# Transcritor de Audio

Transcreve audio para texto fiel em portugues, rodando o Whisper na propria
maquina. O conteudo nunca sai do computador. Feito para os audios longos que
chegam pelo WhatsApp (formato .opus), mas funciona com qualquer arquivo de som.

O trabalho pesado fica em `scripts/transcrever.py`. Este documento orienta como
preparar o ambiente, rodar e o que esperar.

## O que "fiel" significa aqui

O script nao corta, nao resume, nao parafraseia. Transcreve tudo que foi dito.
O Whisper suaviza hesitacao pura (os "ee", "hum", gaguejo), isso e design dele.
Fiel no sentido de conteudo completo, sim. Fiel a cada disfluencia, nao.

## Pre-requisitos

Antes de rodar, garanta que a maquina tem o que precisa. Cheque na ordem:

1. **Python** instalado. Teste no terminal: `python --version`.
2. **ffmpeg** no PATH. Teste: `ffmpeg -version`. Se faltar, no Windows:
   ```
   winget install Gyan.FFmpeg
   ```
   Feche e reabra o terminal depois de instalar.
3. **faster-whisper**:
   ```
   pip install faster-whisper
   ```

Se algum desses faltar quando a pessoa pedir uma transcricao, instale primeiro
e so depois rode. O script ja avisa se o ffmpeg estiver ausente.

## Como rodar

Aponte o script para o arquivo de audio:

```
python scripts/transcrever.py "C:\Users\nome\Downloads\audio.opus"
```

Na primeira execucao o modelo e baixado da internet uma unica vez (o large-v3
tem alguns GB) e fica em cache. As proximas vezes ja partem direto para a
transcricao.

## O que o script faz

1. Confere se o ffmpeg existe.
2. Converte o audio para wav 16kHz mono, o que resolve os containers estranhos
   que o WhatsApp as vezes entrega.
3. Detecta sozinho se ha GPU NVIDIA (transcreve rapido) ou cai para CPU
   (funciona, so mais devagar).
4. Transcreve em portugues, modo fiel, sem cortar nada.
5. Salva um arquivo `.md` ao lado do audio, com o mesmo nome.

## Saida

O arquivo gerado fica na mesma pasta do audio, com a extensao trocada para `.md`.
Estrutura:

```
# Transcricao: nome-do-audio.opus

Data: 2026-06-02 14:30
Duracao: 0:18:42
Modelo: large-v3

---

[transcricao completa, com paragrafos abertos nas pausas longas da fala]
```

## Ajustes

- **Modelo mais rapido**: o padrao e `large-v3`, que da a melhor fidelidade em
  portugues. Se a maquina estiver lenta, troque por `medium` ou `small`:
  ```
  python scripts/transcrever.py "audio.opus" --modelo medium
  ```
  Quanto menor o modelo, mais rapido e menos preciso.

- **Outro idioma**: o padrao e `pt`. Para outro idioma, use `--idioma en`,
  `--idioma es`, etc.

## Notas

- Tudo roda offline depois do download inicial do modelo. Nenhum audio e enviado
  para servico externo.
- Em CPU, audios longos demoram. Um podcast de 30 minutos em CPU pode levar
  varios minutos. Com GPU NVIDIA, e questao de segundos a poucos minutos.
- Se a pessoa quiser tratar a transcricao depois (limpar, estruturar, extrair
  ideias), isso e um passo separado e deve ser pedido a parte. Esta Skill so
  entrega o texto fiel.
