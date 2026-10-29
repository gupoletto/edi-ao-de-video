---
name: editar-video
description: Edita um vídeo pessoal do usuário (vlog, tutorial, Reels/Shorts gravados por ele) com o kit em edicao/ — transcreve, corta pausas e regravações, cria letreiros/títulos/listas no estilo aprendido, legenda, monta e renderiza. Use quando o usuário pedir para editar, cortar, legendar ou "deixar pronto pro YouTube/Instagram" um vídeo que ele gravou. Não é para os Shorts automáticos do canal Fun Stuff (esses usam shorts/pipeline).
---

# Editar um vídeo pessoal

Leia `edicao/ESTILO.md` primeiro (ritmo, os dois estilos, quando usar cada elemento). O vídeo fica em
`edicao/bruto/`; se o usuário mandou o arquivo pelo chat, copie para lá.

Pergunte só o que não der para inferir: estilo (`editorial` = limpo/creme, padrão para YouTube horizontal;
`dinamico` = legendas palavra a palavra, padrão para vertical) e formato (`horizontal` ou `vertical`).

## Passos

0. Vídeo da câmera (iPhone, Android): `python3 edicao/ferramentas/importar.py <arquivo> <v>` (HDR -> SDR, fps fixo;
   arquivo do Google Drive: baixe com `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`).
1. `python3 edicao/ferramentas/transcrever.py edicao/bruto/<v>.mkv --turbo` (o turbo erra bem menos em áudio de rua).
   Corrija na transcrição as frases erradas antes das legendas.
2. `python3 edicao/ferramentas/planejar.py edicao/bruto/<v>.mp4 --estilo <e> --formato <f>`
3. Leia `trabalho/<v>/transcricao.txt` como o "cérebro" do vídeo: marque pessoas, objetos, números, datas e etapas
   citados, e escreva um roteiro de edição curto (o que aparece na tela em cada trecho). Depois preencha em `plano.json`:
   - `elementos` seguindo a tabela da seção 4 do ESTILO (tempos `de`/`ate` do bruto, ancorados no início da frase
     que o elemento ilustra; dure até a frase terminar, 2,5–6 s);
   - `correcoes` para nomes que a transcrição errou;
   - confira os `cortes` de regravação (o detector pode errar; devolva o trecho a `manter` se não for regravação);
   - **tapa/soco na câmera = fim do take** (regra do usuário): nada do que vem depois do tapa volta para `manter`
     ou `abertura`, nem como efeito. O `planejar.py`/`montar.py` cortam sozinhos (`tapas.py`); confira os cortes
     "tapa na câmera" e olhe um quadro de cada para ver se não sobrou camiseta ou chão;
   - clipe que entrou de lado numa faixa vertical (celular deitado gravando em pé): elemento `vertical` com
     `"girar": "anti-horario"` (ou `"horario"`), começando e terminando nas emendas do clipe (`tapas.py` lista);
   - acerte `foco` olhando um quadro (`ffmpeg -ss 5 -i <v> -frames:v 1 q.png`) se o rosto não estiver no centro.
   Rode `planejar.py` de novo só se quiser recalcular os cortes — ele apaga os elementos. Depois de editar o
   JSON à mão, regenere o resumo legível: `python3 -c "import sys;sys.path.insert(0,'edicao/ferramentas');import planejar,comum,os;p='edicao/trabalho/<v>';planejar.escrever_md(p,comum.ler(p+'/plano.json'),comum.ler(p+'/transcricao.json'))"`.
   - `abertura` por último: 1–3 trechos fortes do próprio vídeo (resultado, número, frase de impacto) que vão na frente.
   - trechos **sem fala** que contam a história (b-roll, chegada, show) saem com o corte de pausas: devolva-os a `manter`.
   - procure ideias fora do óbvio na seção 3e do ESTILO antes de repetir o que as referências fazem.
4. **Pare e mostre o plano** (`plano.md`) ao usuário: duração antes/depois, cortes, lista de elementos. Espere a aprovação.
5. `elementos.py --amostra`, olhe os PNGs (texto cortado? destaque certo? erro de digitação?), envie ao usuário os 3 primeiros.
6. `elementos.py`, depois `montar.py --previa --trecho <de> <ate>` num pedaço de ~1 min com elementos variados; aprovado
   o estilo, registre o feedback no ESTILO.md e rode `montar.py --previa` inteiro. Extraia quadros da prévia e confira: elemento no momento certo,
   legenda legível, nada cortado no meio de palavra (ouça os pontos de corte com `ffmpeg -ss`).
   Envie a prévia ao usuário e espere a aprovação ou a lista de correções.
7. `montar.py` (final) -> `edicao/final/<v>_editado.mp4`. Confira com ffprobe (resolução, fps, duração, áudio)
   e envie o arquivo. Se o arquivo passar de ~45 MB, envie também uma cópia em 720p para ver no celular.
   Se o usuário quiser ajustar à mão no Premiere/DaVinci, rode `exportar.py` e envie o .edl e o .csv.

Não faça commit dos vídeos nem de `edicao/trabalho/` (já estão no .gitignore). Commit só de melhorias no kit
ou no ESTILO.md, se o usuário pedir.
