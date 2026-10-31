# Estratégia aprendida de canais que viralizaram (referências de 31/10/2026)

Duas referências enviadas pelo usuário (transcritas em `edicao/trabalho/{monetized,blewup}/`):
- **A — "Claude Code Monetized My YouTube Channel in 14 Days"**: Shorts de 20–30 s em animação 2D com um personagem ("Can we throw our trash into a volcano?"). Monetizou em 2 semanas, com 3 milhões de views a cada 48 h.
- **B — "I Blew Up a YouTube Channel in 7 Days with AI"** (Jack Craig): histórias animadas de jogos do Roblox. Chegou a 150 mil views e 1.000 inscritos com o 2º Short.

## 1. Nicho = tema provado + apresentação diferente
- Pegue um tema que já tem audiência e apresente num estilo que quase ninguém usa nele. Em A, um assunto de vídeo antigo de curiosidade virou animação 2D, e a versão 2D fez 3,6 milhões.
- B: "ideias originais não ganham no YouTube; execução melhor ganha". Não copie o canal de referência (um canal já estabelecido ocupa o espaço). Melhore a estrutura.
- **Para nós:** já fazemos isso com simulação de verdade e 3D. O próximo passo é **um personagem recorrente desenhado por código** (cairo/vetor, nada de imagem de IA) contando os "what if / why". Isso dá marca ao canal: B lembra que um personagem reconhecível ajuda a monetizar fora dos anúncios.

## 2. Pesquisa de ideias (complementa o passo 3 da ROTINA)
- **Decupar os Shorts de maior sucesso do tema:** o que acontece em cada cena, quanto dura, o título e as views. Os padrões aparecem rápido (em B, todo gancho tinha movimento no 1º quadro).
- **Outlier de comentários:** um Short com bem mais comentários do que o normal para as views dele revela o que o público quer discutir. Como referência, 16 mil comentários em 30 milhões de views, quando o esperado seria ~6 mil. Calcule `comentários / views` nas buscas e use o tema do outlier no roteiro.
- **Canal pequeno com picos enormes logo nos primeiros uploads** = conceito que ressoa (em B, "hacker/admin abusando do poder").

## 3. Roteiro com arco de conflito (não linear)
- **Linear** (gancho → ação → recompensa) é previsível.
- **Arco de conflito:** gancho → subida → **conflito** → **virada** → subida → recompensa.
- **Arco em loop:** dois conflitos, cada um com sua virada.
- O conflito e a virada tiram a previsibilidade e aumentam a retenção e o engajamento.
- **Em cada formato nosso:**
  - **What if / why:** "tentamos X" → "deu errado por causa de Y" (conflito) → "mas e se Z?" (virada) → resultado.
  - **Ranking:** um item que parece ganhar e é ultrapassado (conflito no #2).
  - **Quiz:** uma rodada com pegadinha.
- **Manter realista:** em B, o conflito exagerado (hacker) gerou comentários negativos. Conteúdo "novidade/gimmick" morre rápido e não constrói marca.

## 4. Execução
- **Gancho com movimento já no 1º quadro.** Nada de tela parada com título.
- **Cortes de 1 a 3 s** para manter o ritmo.
- **Desenho de som por ação:** passos, voz do personagem, impactos. Música por baixo.
- **Duração de A:** 20–30 s (mais barato de produzir e retém melhor). Os nossos têm ficado entre 34 e 51 s. Para what if/why e ranking, buscar 25–35 s.

## 5. Publicação
- **Título:** simples e descritivo, com 2 emojis. Descrição curta + `#shorts`, poucas tags, "made for kids" = não. Já fazemos isso.
- **Métricas de Shorts:**
  - **Taxa de visualização** (quem viu vs. quem deslizou): alvo ≥ 80 %. 60 % é normal só no 1º upload de canal novo.
  - **Duração média da visualização.**
  - **Leitura:** a 1ª onda do algoritmo é teste. Vídeo com métricas boas costuma ganhar outras "pernas" dias depois.
  - **Requisito:** essas métricas vêm da YouTube Analytics API, que precisa do escopo `yt-analytics.readonly`. O nosso refresh token ainda não tem.
- **Cadência (opinião de B, sem teste controlado):** nos 5 primeiros uploads, esperar ≥ 48 h entre vídeos e publicar o próximo só quando o anterior ficar < 100 views/h por 12 h. B conta que um Short publicado no meio do embalo de outro flopou, e o mesmo vídeo republicado depois fez 13 milhões. **Conflita com o nosso PLANO (3 por dia).** Decisão do usuário. Não mudar sozinho.
- **1º upload de canal novo:** é a única vez que "sorte" pesa. Não desanimar.

## 6. Pipeline de A (por referência)
Claude Code + MCP do Higgsfield geram o personagem em todas as poses (PNG sem fundo). Antes de animar, um "mood board". O código anima os PNGs no Remotion, com efeitos sonoros, música e voz.

Nossa versão compatível com o PLANO troca o gerador de imagens por **poses desenhadas em código**: um módulo `personagem.py` com corpo, rosto e expressões parametrizados, que pode ser animado quadro a quadro. Fica 100% original e sem `containsSyntheticMedia`.
