# Rotina diária de produção (instruções para a sessão agendada)

Leia `shorts/PLANO.md` (documento-mestre: nicho, marca, catálogo de formatos, regras de qualidade, métricas e decisões), `shorts/TOPICOS.md` e `shorts/ESTRATEGIA.md` antes de começar. As regras de monetização dele valem acima de tudo: na dúvida, produza menos vídeos, nunca um vídeo que as viole.

## 0. Preparação

- Trabalhe na branch `claude/focused-einstein-6l079f` (`git fetch origin claude/focused-einstein-6l079f && git checkout claude/focused-einstein-6l079f`) e faça push só nela.
- Credenciais (variáveis de ambiente): `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (escopos `youtube.upload` + `youtube.readonly`), Opcional: `PIXABAY_API_KEY` para cenas reais (a Pexels suspendeu novas chaves). A rede do ambiente bloqueia Pexels, Pixabay, ElevenLabs, OpenAI e Hugging Face, a menos que o usuário libere o domínio. GitHub, PyPI, npm e googleapis funcionam.
- Todo o visual é gerado por código. Cenas reais do Pixabay só entram se `PIXABAY_API_KEY` existir e pixabay.com responder, e no máximo 1 vídeo por dia.

## 1. Pendências

Para cada `shorts/lote-*/` com vídeo que ainda não está no `uploaded.json`, rode `python3 shorts/upload.py <lote>`. O script coloca no próximo horário de pico livre os vídeos sem data ou com data já passada.

## 2. Pipeline

O código de produção fica em `shorts/pipeline/`. Se ainda não existir (primeira execução), construa-o e faça commit:

- **Roteiro → cenas → voz → legendas → render** em 1080×1920, 30 fps, 20–60 s, H.264 + AAC, volume em −14 LUFS, arquivo < 40 MB.
- **Estilo:** cabeçalho no topo, legenda palavra por palavra, voz animada em inglês, layout dentro da área segura dos Shorts (`core.AREA` e `core.LEGENDA_Y`; não use coordenadas fixas fora de `AREA`). Os formatos e as receitas estão no `PLANO.md`, seção 3, com um episódio de referência para cada um.
- **Visual 100% original por código** (numpy/Pillow/matplotlib/cairo + ffmpeg, ou Remotion local; Chromium está instalado). Monte módulos reaproveitáveis para os tópicos de `TOPICOS.md`: mapas e linhas do tempo (história, países; use dados geográficos abertos de pacotes do PyPI, como `geopandas`/Natural Earth, ou do GitHub), ilusões de ótica, simulações de física e de espaço (integração numérica de verdade), comparação de tamanho, Terra e natureza (vulcões, placas, ondas, clima), satisfying (`satisfying.py`; nos quizzes de enchimento use `satisfying.capacidade`) e gráficos de dados. Sempre dentro do nicho do `PLANO.md`.
- Os **formatos** do dia: ranking (#5 → #1, com o conflito no #2), "what if / why" contado pelo mascote Quark, interativo (quiz com uma rodada pegadinha) e 3D "como funciona".
- **Todo vídeo termina com `personagem.seg_pergunta(fala, título, fundo=…)`**: o Quark entra, acena e faz a pergunta final. É a assinatura do canal.
- **Mascote Quark** (`pipeline/personagem.py`, desde 02/11/2026). Feijão amarelo com óculos de laboratório; `quark(ctx, x, y_pés, altura, Pose(...), t)` com expressões neutro, feliz, rindo, surpreso, medo, pensando, bravo, tonto e determinado. Também tem braços, caminhada/corrida, pulo, squash, capacete e suor. A boca segue a voz: `Pose(boca=boca_da_voz(seg, t))`. Referência: `pipeline/episodes/quark_jupiter.py`.
  - O Quark narra em 1ª pessoa ("What if I jumped into Jupiter?"), e o título usa "you".
  - Arco de conflito: gancho → subida → conflito → prova/fato real → virada → recompensa → pergunta final.
  - 25–35 s, com cenas cheias de movimento desde o 1º quadro.
  - Quark grande (≥ 440 px de altura), com os pés até ~1260 px (acima da legenda) e a cabeça abaixo de ~440 px (abaixo do cabeçalho).
  - Ele nunca morre nem se machuca de verdade: o perigo vira humor e ele escapa.
  - Fatos com números conferidos (docstring do episódio).
- **Formato 3D "how it works"** (incluído a pedido do usuário em 30/10/2026; em alta no Brasil e nos EUA, mediana de ~113 mil em "how it works 3d animation"): um objeto em 3D de verdade (three.js renderizado no Chromium headless, `pipeline/tres.py` + uma cena em `pipeline/cenas3d/`), com física/cinemática real calculada no Python, câmera girando devagar e cada etapa narrada sincronizada com o movimento. Referência: `pipeline/episodes/tres_motor.py` (motor de 4 tempos). Tem dia fixo na agenda (quinta). Pode entrar em mais 1 dia da semana cujo tópico tenha um mecanismo para mostrar (relógio, eclusa, catapulta, olho humano, foguete, vulcão…). Ideia de abertura aprendida (referência "Claude Motion", 30/10): o objeto nasce como blueprint (linhas brancas sobre fundo azul-petróleo, cotas), ganha material e acende/liga. Escreva a cena como especificação: estilo com cores em hex + linha do tempo em segundos. Enquadramento: o objeto inteiro entre o cabeçalho (~20 % do topo) e as legendas (~75 %); confira com quadros de teste (`Filme.renderizar(..., tempos=[...])`) antes do render completo (~4 min).
- **Voz:** Kokoro, TTS gratuito e de boa qualidade que roda offline. `pip install kokoro-onnx soundfile` e baixe do GitHub `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx` e `voices-v1.0.bin` (o Hugging Face está bloqueado). Voz animada em inglês americano, como `am_michael` ou `af_heart`; use sempre a mesma no canal. Cache dos modelos em `~/.cache/kokoro` (fora do Git).
- **Música:** sintetizada pelo próprio pipeline ou nenhuma. Nunca use música baixada.

## 3. Tendências

Use um access token (`upload.py` tem `access_token`) e `search.list` com `type=video`, `videoDuration=short`, `publishedAfter` = 7 dias atrás, `order=viewCount`, `relevanceLanguage=en`, `regionCode=US`, `maxResults=25`, seguido de `videos.list?part=statistics,snippet` nos resultados. Compare tópicos pela **mediana** de views e descarte resultados fora do tema, infantis ou em outra língua.

- **Todo dia:** 1 a 3 buscas dentro do tópico de amanhã (veja a agenda em `TOPICOS.md`), para achar subtemas e formatos que estão subindo agora.
- **Todo domingo:** meça de novo os tópicos do nicho em `TOPICOS.md` e mais até 5 candidatos novos **dentro do nicho** que tenham aparecido nas buscas da semana. Reordene o top 10, refaça a agenda da semana seguinte e atualize a data no topo do arquivo.
- **Troca no meio da semana:** se o tópico de amanhã caiu para menos da metade da mediana anterior e uma reserva está bem acima, use a reserva e atualize a agenda.
- **Desempenho do próprio canal:** rode `python3 shorts/metricas.py` e cole a saída em `tendencias/AAAA-MM-DD.md`. Ela traz views, engajamento, duração média, % assistida (YouTube Analytics, atrasa 2–3 dias) e o resumo por formato e por tópico, e marca os vídeos "presos na amostra". Use o resumo para decidir (regras no `PLANO.md`, seção 6). Depois de 2 semanas de dados, a média do canal vale metade da nota de cada tópico. Se o Analytics der 403, siga com as estatísticas públicas e avise no relatório.
- **Domingo 08/11:** `python3 shorts/metricas.py --desde 2026-11-02 --ate 2026-11-08` vs `--desde 2026-10-27 --ate 2026-11-01`. Escreva a comparação do teste de 2 por dia e recomende ao usuário (manter 2, voltar para 3 ou testar 1). Ele decide.
- vidIQ (se as ferramentas existirem): no máximo 1 chamada por dia, e só se `vidiq_balance` ≥ 5.
- Salve um resumo em `shorts/tendencias/AAAA-MM-DD.md`.

## 4. Escolha dos vídeos de amanhã

- **Quantos:** rode `python3 shorts/upload.py --free-slots <data de amanhã>` e produza exatamente esse número de vídeos (no máximo 3). Assim nada se acumula para os dias seguintes.
- **Tópico:** o de amanhã na agenda de `TOPICOS.md`, com os formatos que ela indica para o dia (no teste de 02 a 08/11: Quark + ranking/interativo/3D), cada um com um subtema diferente. Sempre dentro do nicho "ciência visual e simulações satisfatórias".
- Consulte `shorts/historico.md` (crie se não existir): nenhum subtema repetido em 30 dias, nem padrão de título em dias seguidos. Respeite os "Cuidados por tópico" de `TOPICOS.md`.
- Inspire-se no que está subindo, mas faça a sua versão original. Nunca copie o vídeo de outro canal.
- Aplique `shorts/ESTRATEGIA.md` (aprendido em 31/10/2026):
  - nas buscas, calcule `comentários/views` e use o tema dos outliers;
  - roteiro com arco de conflito (gancho → subida → conflito → virada → recompensa), não linear;
  - movimento já no 1º quadro;
  - what if/why e ranking com 25–35 s;
  - as 3–4 primeiras palavras do título dizem o tema;
  - descrição com 1 frase-resumo + 5–6 palavras-chave separadas por vírgula;
  - `#shorts` + 2–3 hashtags;
  - pergunta final que convida a discordar, sem nunca distorcer os fatos.

## 5. Produção e conferência (obrigatório para cada vídeo)

- `ffprobe`: 1080×1920, duração dentro do alvo do formato (`PLANO.md`, seção 3; nunca acima de 60 s), faixa de áudio presente.
- Área segura: em 2 quadros com texto, rode `python3 anuncios/zonas.py --conferir <vídeo> --em <s> --zona shorts` e confira que título, legenda e números ficam dentro do retângulo verde.
- O 1º quadro já tem movimento, e o último segmento é o `seg_pergunta` do Quark.
- Extraia ~6 quadros (`ffmpeg -vf fps=…`) e **olhe as imagens**: texto cortado ou ilegível, tela preta, cena que não bate com o item narrado, marca d'água de terceiros.
- Fatos do roteiro (números, temperaturas) precisam estar corretos.
- Reprovou e não deu para consertar? Não publique o vídeo. Registre o motivo no relatório.

## 6. Publicação

- Crie `shorts/lote-AAAA-MM-DD/videos.json` no mesmo formato do lote 01: title ≤ 100 caracteres, **descrição curta** (1 frase-resumo, a lista do ranking se houver, 1 pergunta para comentários, 1 linha com 5–6 palavras-chave separadas por vírgula, "Animation: Fun Stuff · Voiceover: AI voice." e `#shorts` + 2–3 hashtags; sem lista de links; se usar cenas de banco de imagens, só 1 linha "Footage: Pixabay (free license)"), tags, `publishAt` = os horários que o `--free-slots` devolveu, um por vídeo, `containsSyntheticMedia` correto.
- Rode `python3 shorts/upload.py shorts/lote-AAAA-MM-DD`.
- Adicione em `shorts/historico.md` a data, o tópico, o subtema e o formato de cada vídeo.
- **Commit:** só o que é leve (`videos.json`, `uploaded.json`, roteiros, tendências, histórico, pipeline). Os `.mp4` estão no `.gitignore`. Se o upload não aconteceu, adicione-os com `git add -f` para a próxima execução enviar. Faça push para `claude/focused-einstein-6l079f`.

## 7. Relatório final (curto, em português)

**Notificação no celular (obrigatório, o usuário pediu):** carregue a ferramenta `PushNotification` com `ToolSearch` (`select:PushNotification`) e envie um resumo de 1 a 2 linhas, por exemplo: "Fun Stuff: 3 Shorts agendados para amanhã (tópico: Espaço) · 13h, 16h, 20h. Tudo certo." Em caso de falha, a notificação diz o que falhou. Se a ferramenta não existir, registre isso no relatório.

Liste os vídeos agendados (título, horário em Brasília, link), o tópico do dia e por quê, mudanças no top 10 (se houve), como foram os vídeos anteriores e qualquer falha.
