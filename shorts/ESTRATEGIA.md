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

---

# Referências de 31/10/2026 (2ª leva)

Transcrições em `edicao/trabalho/{postar_shorts,algoritmos}/`:
- **C — "O jeito CERTO de postar Shorts no YouTube"** (canal de cortes de animação, 50 mil inscritos);
- **D — "How Social Media Algorithms Actually Work"** (Callaway, 1 mi de seguidores).

## 7. Como o algoritmo decide (D)
1. **Mapa do tema:** a plataforma "assiste" ao vídeo. Lê a imagem (visão computacional), o áudio/transcrição e os metadados (título, descrição, hashtags, criador).
2. **Fit score:** com esse mapa, ela prevê quem vai gostar e mostra o vídeo a uma **amostra de ~200 pessoas**, quase todas **não inscritas**.
3. **Resultado da amostra:**
   - bom → empurra para 2 mil, 20 mil, 200 mil… até os dados enfraquecerem;
   - neutro → refaz o fit score e testa outra amostra de ~200;
   - ruim → para quase na hora. Esse é o "presídio das 200 views", e talvez explique o nosso teto de ~1,1 mil.
4. **As 3 métricas da amostra:**
   - tempo médio assistido (e % concluída);
   - **taxa de engajamento** = (likes + comentários + compartilhamentos) / views;
   - fatia da sessão do espectador gasta nos seus vídeos (não dá para ver).

## 8. Consistência de público é a alavanca principal (D)
- **"Audience matching":** fazer sempre vídeos do **mesmo tema estreito para o mesmo perfil de espectador**. Assim o algoritmo aprende a quem mostrar e acerta a amostra.
- **Temas variados confundem o algoritmo:** tecnologia, saúde e política em sequência geram uma amostra misturada e o vídeo seguinte flopa. Até **um viral fora do público principal** atrapalha os vídeos seguintes. É preciso dizer não a ideias "virais" que atraem outro público.
- **Para nós:** isso questiona o rodízio de um tópico diferente por dia (ilusões → espaço → física → geografia → tamanho → satisfying → mitologia).
  - Os nossos melhores ficam todos no guarda-chuva **"ciência visual e simulações satisfatórias"**: ilusões, física, espaço, tamanho e o 3D "como funciona".
  - Mitologia, dinossauros e história fogem desse público.
  - Ainda não decidido (precisa do ok do usuário): **estreitar o canal para esse guarda-chuva**.
- Estude o que funciona no nicho com **pontuação de outlier** (views do vídeo / média do canal).

## 9. O que faz a amostra engajar (D)
- Tema relevante para o espectador ideal.
- Informação **não óbvia**.
- Fácil de absorver.
- Algo que dá para "usar" logo. Nos nossos Shorts, um fato para contar a alguém ou um teste para fazer na hora.

**Comentários:**
- tomar posição firme, sem ficar em cima do muro;
- escolher o lado do contra (quem discorda comenta);
- amplificar a afirmação;
- falar de coisas que todo mundo já tem opinião (marcas, ídolos);
- provocar emoção.
- **No nosso caso:** "o #1 é o mais satisfatório, discorda?" no ranking; "a maioria erra a rodada 3" no quiz; o pior-caso polêmico no what-if. Sempre sem desinformação: a posição é sobre opinião, nunca sobre os fatos.

## 10. Mecânica de postagem (C)
- **Título:** as **3–4 primeiras palavras** são as que aparecem no feed. Elas precisam ser fortes e dizer o tema. C sugere MAIÚSCULAS no começo do canal (opcional).
- **Hashtags:** poucas. Muitas hashtags em canal novo parecem spam. `#shorts` + 2–3 do tema.
- **Descrição:** 1 frase que resume o Short + 5–6 palavras-chave da busca, separadas por vírgula. Tags: várias. Pesam pouco, mas ajudam no público.
- **Processamento:** subir como privado/não listado e só publicar depois de 20–30 min, quando o HD estiver processado. Um vídeo borrado no 1º impacto é pulado. **Já fazemos isso:** o `upload.py` sobe privado com `publishAt` horas depois.
- **Capa do Short:** um quadro chamativo. Faça cada vídeo ter um momento visualmente forte. Pelo app dá para escolher o quadro; pela API o 1º quadro pesa mais, então o gancho visual precisa estar no começo.
- **Pedidos de C que NÃO seguimos:**
  - "adicionar música viral, mesmo no volume zero": viola a regra de música do PLANO, e a API não permite;
  - "esconder contagem de likes": a API não tem esse campo.
- **Horário:** C diz que horário incomum (19h, 21h, 22h) ajuda no começo; D diz que horário não importa. **Nossa regra:** seguir os dados do próprio canal quando houver.

## 11. Conclusão das 4 referências
O "bolo" é: tema estreito e consistente para um público + gancho visual + roteiro com conflito + informação não óbvia. Horário, hashtags e legenda são "cobertura".
