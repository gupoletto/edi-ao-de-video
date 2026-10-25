# Rotina diária de produção (instruções para a sessão agendada)

Leia `shorts/PLANO.md` antes de começar. As regras de monetização dele valem acima de tudo: na dúvida, produza menos vídeos, nunca um vídeo que as viole.

## 0. Preparação

- Trabalhe na branch `claude/focused-einstein-6l079f` (`git fetch origin claude/focused-einstein-6l079f && git checkout claude/focused-einstein-6l079f`) e faça push só nela.
- Credenciais (variáveis de ambiente): `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (escopos `youtube.upload` + `youtube.readonly`), Opcional: `PIXABAY_API_KEY` para cenas reais (a Pexels suspendeu novas chaves). A rede do ambiente bloqueia Pexels, Pixabay, ElevenLabs, OpenAI e Hugging Face, a menos que o usuário libere o domínio. GitHub, PyPI, npm e googleapis funcionam.
- Sem `PIXABAY_API_KEY` ou sem acesso a pixabay.com: os 3 vídeos do dia são originais (A, B-original e C, veja abaixo). Avise no relatório o que está faltando só se afetar o resultado.

## 1. Pendências

Para cada `shorts/lote-*/` com vídeo que ainda não está no `uploaded.json`, rode `python3 shorts/upload.py <lote>`. O script coloca no próximo horário de pico livre os vídeos sem data ou com data já passada.

## 2. Pipeline

O código de produção fica em `shorts/pipeline/`. Se ainda não existir (primeira execução), construa-o e faça commit:

- **Roteiro → cenas → voz → legendas → render** em 1080×1920, 30 fps, 20–60 s, H.264 + AAC, volume em −14 LUFS, arquivo < 40 MB.
- Os 5 vídeos de `shorts/lote-01/` são a referência de estilo: título do ranking no topo, número grande em cada item (#5 → #1), legenda palavra por palavra, voz animada em inglês.
- **Tipo A/C** (original): simulação e animação geradas por código (numpy + renderização de quadros + ffmpeg, ou Remotion local; Chromium está instalado). Física de verdade (integração numérica), não animação fingida.
- **Tipo B**: se `PIXABAY_API_KEY` existir e pixabay.com responder, use cenas da API `https://pixabay.com/api/videos/` sobre o tema em alta (guarde autor + URL para a descrição). Senão, faça a versão **original** do tema em alta: simulação procedural "satisfying" ligada a ele (ex.: "lava" → simulação de partículas de lava engolindo objetos; "gelo" → rachaduras se propagando; "fábrica" → esteira e máquinas animadas; bolinha em espiral, dominós, areia, fluidos, ordenação de cores).
- **Voz:** Kokoro, TTS gratuito e de boa qualidade que roda offline. `pip install kokoro-onnx soundfile` e baixe do GitHub `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx` e `voices-v1.0.bin` (o Hugging Face está bloqueado). Voz animada em inglês americano, como `am_michael` ou `af_heart`; use sempre a mesma no canal. Cache dos modelos em `~/.cache/kokoro` (fora do Git).
- **Música:** sintetizada pelo próprio pipeline ou nenhuma. Nunca use música baixada.

## 3. Tendências

1. Pegue um access token (`upload.py` tem a função `access_token`). Chame `search.list` (`type=video`, `videoDuration=short`, `publishedAfter` = 7 dias atrás, `order=viewCount`, `relevanceLanguage=en`, `regionCode=US`) para 5 a 10 consultas do nicho: "ranking satisfying", "physics simulation", "satisfying moments", além de temas novos que apareçam. Depois rode `videos.list?part=statistics` nos resultados.
2. vidIQ: no máximo 1 chamada (`vidiq_outliers` ou `vidiq_trending_videos`, Shorts, em inglês), e só se `vidiq_balance` ≥ 5.
3. Desempenho do próprio canal: rode `videos.list?part=statistics` nos IDs de todos os `uploaded.json`. Anote quais temas e formatos foram melhor.
4. Salve um resumo em `shorts/tendencias/AAAA-MM-DD.md`: temas em alta, números, o que funcionou no canal.

## 4. Escolha dos 3 vídeos de amanhã

- Um de cada tipo: A, B e C (veja a agenda no PLANO).
- Consulte `shorts/historico.md` (crie se não existir): nada de repetir tema em 14 dias, nem padrão de título em dias seguidos.
- Dê preferência a temas em alta, com a sua própria versão original. Nunca copie o vídeo de outro canal.

## 5. Produção e conferência (obrigatório para cada vídeo)

- `ffprobe`: 1080×1920, duração de 20–60 s, faixa de áudio presente.
- Extraia ~6 quadros (`ffmpeg -vf fps=…`) e **olhe as imagens**: texto cortado ou ilegível, tela preta, cena que não bate com o item narrado, marca d'água de terceiros.
- Fatos do roteiro (números, temperaturas) precisam estar corretos.
- Reprovou e não deu para consertar? Não publique o vídeo. Registre o motivo no relatório.

## 6. Publicação

- Crie `shorts/lote-AAAA-MM-DD/videos.json` no mesmo formato do lote 01: title ≤ 100 caracteres, descrição com créditos e hashtags, tags, **sem `publishAt`** (o `upload.py` coloca cada vídeo no próximo horário de pico livre), `containsSyntheticMedia` correto.
- Rode `python3 shorts/upload.py shorts/lote-AAAA-MM-DD`.
- Adicione os temas em `shorts/historico.md`.
- **Commit:** só o que é leve (`videos.json`, `uploaded.json`, roteiros, tendências, histórico, pipeline). Os `.mp4` estão no `.gitignore`. Se o upload não aconteceu, adicione-os com `git add -f` para a próxima execução enviar. Faça push para `claude/focused-einstein-6l079f`.

## 7. Relatório final (curto, em português)

Liste os 3 vídeos agendados (título, horário em Brasília, link), as tendências que guiaram a escolha, como foram os vídeos anteriores e qualquer falha ou credencial faltando.
