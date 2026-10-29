# Edição dos seus vídeos pessoais

O mesmo método dos vídeos de referência (veja `ESTILO.md`): você grava e pede; a IA transcreve, planeja,
cria os elementos, monta e renderiza. Tudo roda aqui, sem programa de edição, com ffmpeg + Python.

## Pastas

| Pasta | O que vai nela |
|---|---|
| `bruto/` | o vídeo como você gravou |
| `estilo/` | suas referências visuais (logo, prints de vídeos que você gosta) — opcional |
| `trabalho/<nome>/` | transcrição, plano, elementos e prévia (gerados) |
| `final/` | o vídeo pronto |

Os vídeos e arquivos gerados não vão para o Git.

## Pedindo ao Claude

Coloque o arquivo em `edicao/bruto/` e peça, por exemplo:

> Edite o vídeo `bruto/viagem.mp4` no estilo editorial, horizontal, para o YouTube.

> Transforme `bruto/receita.mp4` num Reels vertical no estilo dinâmico, com legendas.

O Claude segue as etapas e para duas vezes para você aprovar: **no plano** e **na prévia**.

## Etapas (se quiser rodar à mão)

```bash
python3 edicao/ferramentas/importar.py    ~/Downloads/IMG_1234.MOV viagem  # 1. HDR/VFR -> bruto/viagem.mkv
python3 edicao/ferramentas/transcrever.py edicao/bruto/viagem.mkv --turbo  # 2. transcrição com tempos
python3 edicao/ferramentas/planejar.py    edicao/bruto/viagem.mp4 --estilo editorial --formato horizontal
#   3. revise edicao/trabalho/viagem/plano.md; os elementos visuais entram em plano.json -> "elementos"
python3 edicao/ferramentas/elementos.py   edicao/bruto/viagem.mp4 --amostra # 4. um quadro de cada elemento
python3 edicao/ferramentas/elementos.py   edicao/bruto/viagem.mp4           #    renderiza os elementos
python3 edicao/ferramentas/montar.py      edicao/bruto/viagem.mp4 --previa --trecho 30 90   # 5. aprove 1 min
python3 edicao/ferramentas/montar.py      edicao/bruto/viagem.mp4 --previa  #    prévia inteira (540p)
python3 edicao/ferramentas/montar.py      edicao/bruto/viagem.mp4           # 6. final -> edicao/final/
python3 edicao/ferramentas/montar.py      edicao/bruto/viagem.mp4 --4k      #    versão 2160p p/ o YouTube
python3 edicao/ferramentas/exportar.py    edicao/bruto/viagem.mp4           #    opcional: EDL p/ Premiere/DaVinci
```

Dependências: `pip install sherpa-onnx pycairo numpy` e ffmpeg. Na primeira transcrição o modelo
Whisper small (~640 MB, do GitHub do sherpa-onnx) é baixado para `~/.cache/sherpa`; as fontes (OFL)
vão para `~/.local/share/fonts`.

## Ajustes no plano (`trabalho/<nome>/plano.json`)

- `manter`: trechos do bruto que ficam (em segundos). Apague ou mude um trecho para cortar/manter algo.
- `cortes`: o que foi tirado e por quê (pausas, regravações, tapa na câmera) — só informativo.
- **Tapa na câmera = fim do take** (combinado com o usuário). `tapas.py` acha o tapa (mão cobrindo a lente +
  pancada no áudio) e as emendas entre clipes. O `planejar.py` e o `montar.py` tiram tudo do tapa até o próximo
  clipe, e os restos de menos de 0,6 s de outro clipe, mesmo de trechos postos à mão em `manter` ou `abertura`.
  Para conferir: `python3 edicao/ferramentas/tapas.py edicao/bruto/<v>.mkv`.
- `zooms`: trechos com zoom de 110 % no rosto. `foco`: onde está o rosto (fração da largura e da altura).
- `legendas`: liga/desliga; `legenda_estilo`: `palavra` (1–3 palavras, contorno), `frase` (palavra-chave em serifa
  itálica) ou `caixa`. `correcoes`: palavras que a transcrição errou, para as legendas.
- `abertura`: trechos do bruto `[[de, ate], ...]` que vão para o começo como gancho (o resto do vídeo segue igual).
- `sons`: efeitos sonoros sintetizados (whoosh nos cards, "pop" nos itens). Sem direitos autorais.
- `abafar`: trechos do bruto com o som "de longe" (passa-baixa e mais baixo), p.ex. música de show de terceiros.
- `elementos`: `titulo`, `lista`, `numero` (com `contar_de`), `letreiro` (`"~texto~"` sai riscado), `sumario`,
  `dividido`, `progresso`, `selo`, `tela`, `foco` (com `contorno: false` vira faixa de cinema), `popup`,
  `vertical` (clipe vertical com laterais desfocadas). Campos em `ferramentas/elementos.py`.
  Os tempos `de`/`ate` são do vídeo **bruto**; o montador converte para o editado.

## Qualidade e sincronia

- Mande o arquivo **original da câmera** (pelo Google Drive), não o exportado por outro app. O `importar.py`
  converte HDR em SDR e fixa a taxa de quadros; todas as etapas usam compressão quase sem perda e o final sai
  em H.264 crf 18 (`--crf 16` para ainda mais qualidade).
- Os cortes caem na grade de quadros e o áudio é cortado com `atrim` (exato até a amostra), com o mesmo início
  e fim do vídeo: cada trecho tem a mesma duração nos dois. O montador para com erro se vídeo e áudio da linha
  do tempo divergirem em mais de 1 quadro.

## Limites desta versão

- O tempo de cada palavra é estimado dentro da frase (a frase em si tem tempo exato), então a legenda
  palavra a palavra pode adiantar ou atrasar um pouco em frases longas.
- Ainda não faz: recorte do fundo atrás de você (texto atrás da pessoa), trilha musical e b-roll de bancos
  de imagem. Dá para acrescentar quando você precisar.
- A montagem é em duas passadas: primeiro a linha do tempo (`trabalho/<nome>/linha_do_tempo.mkv`), depois as camadas.
