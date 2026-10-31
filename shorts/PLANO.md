# Plano do canal Fun Stuff (@funstuff-67)

> Documento-mestre, alinhado em 31/10/2026 a partir dos resultados do canal e das 4 referências estudadas
> (`ESTRATEGIA.md`). A rotina diária (`ROTINA.md`) executa este plano; a agenda de tópicos fica em `TOPICOS.md`; o que
> já foi publicado fica em `historico.md`.

## 1. Identidade

- **O quê:** Shorts em inglês para o público dos EUA, com visual 100 % original gerado por código e voz de IA.
- **Nicho: ciência visual e simulações satisfatórias.** É sempre o mesmo espectador: curioso por ciência, que gosta de
  *ver a coisa acontecer*. O algoritmo testa cada vídeo com ~200 pessoas parecidas com quem já gostou do canal, e
  tópicos espalhados estragam essa amostra (`ESTRATEGIA.md`, seções 7 e 8). Os tópicos permitidos e os proibidos estão
  em `TOPICOS.md`.
- **Marca: o mascote Quark.** Feijão amarelo com óculos de laboratório na testa, desenhado em código
  (`pipeline/personagem.py`). Ele apresenta os "what if / why" e fecha **todos** os vídeos com a pergunta final
  (`seg_pergunta`). Assim todo Short do canal é reconhecível em 1 segundo.
- **Promessa:** em menos de 40 s você vê algo acontecer na tela e sai com um fato que dá vontade de contar para alguém.

## 2. Situação e meta

- Canal criado em 25/10/2026. Com o formato atual, os vídeos ficam entre **~1.000 e 1.250 views** e travam aí. O lote 1
  (satisfying genérico) ficou em dezenas.
- **Meta: entrar no YPP sem ser recusado na revisão.** O programa exige 1.000 inscritos + 10 milhões de views
  válidas de Shorts em 90 dias. A revisão é humana e olha o canal inteiro.
- **O próximo degrau é sair da "amostra"** (~1 mil views) para a 2ª e 3ª onda de distribuição (10 mil+). Para isso:
  público consistente, gancho visual no 1º quadro, roteiro com conflito e retenção acima de 70 %.

## 3. Catálogo de formatos

Todo vídeo tem 1 tópico do dia, 1 subtema que não se repetiu em 30 dias e 1 destes formatos.

| Formato | Para quê | Receita | Código de referência |
|---|---|---|---|
| **Ranking** (#5 → #1) | O formato mais estável do canal (~1,2 mil) | 5 itens, cada um com uma cena animada. O conflito vem no **#2**: parece que ganha e é superado. O #1 é o mais visual. | `episodes/sat_loops_ranking.py`, `space_extreme_planets.py` |
| **What if / why com o Quark** | Personagem + história: o formato que mais cresce nas referências | Arco de conflito: gancho (Quark em ação no 1º quadro) → subida → **conflito** → prova (fato real) → **virada** → recompensa → pergunta. Quark narra em 1ª pessoa. | `episodes/quark_jupiter.py` |
| **Interativo** (quiz) | Comentários ("comment your score") | 3 a 5 rodadas com contagem 3-2-1. Uma rodada é **pegadinha** ("most people get this wrong"). A resposta sai da simulação ou de dados reais. | `episodes/sat_fill_quiz.py`, `geo_guess_shape.py`, `quiz.py` |
| **Como funciona em 3D** | Mecanismos: alta demanda ("how it works 3d") | Objeto 3D real (three.js), física calculada no Python, câmera girando devagar, cada etapa narrada. Abertura "blueprint → material". O Quark pode aparecer em 2D só na pergunta final. | `episodes/tres_motor.py`, `tres.py`, `cenas3d/` |

**Regras que valem para todos os formatos**
- **Duração:** 25–35 s para Quark e ranking; quiz até 50 s; 3D até 45 s. Nunca acima de 60 s.
- **1º quadro já em movimento:** nada de tela parada com título. O título aparece *sobre* a ação.
- **Cortes e mudanças visuais a cada 1–3 s.** Efeito sonoro em cada ação (whoosh, tick, ding); música sintetizada
  por baixo.
- **Layout dentro da área segura dos Shorts:** cabeçalho em 190–410 px, cena em 440–1270 px, legenda até 1430 px,
  nada importante nos 10 % da direita. O `core.py` já faz isso; confira com
  `python3 anuncios/zonas.py --conferir <vídeo> --em <s> --zona shorts`.
- **Final:** `seg_pergunta` com uma pergunta que **convida a discordar** ("which one was your #1?", "Jupiter or
  Saturn?"), sem distorcer fatos. Se der, a última cena emenda no começo (loop).
- **Fatos conferidos:** números e fontes na docstring do episódio.

## 4. Agenda e cadência

- **Horários:** um pouco antes dos picos dos EUA, no horário de Nova York (o `upload.py` ajusta o horário de verão).
  - Padrão, 3 por dia: dias úteis 12h · 15h · 19h; fim de semana 10h · 14h · 19h.
  - **Teste de 02 a 08/11, 2 por dia:** dias úteis 12h · 19h; fim de semana 10h · 19h. Em Brasília, 14h e 21h nos
    dias úteis; 12h e 21h no fim de semana.
- **Um tópico por dia da semana** (agenda em `TOPICOS.md`):

| Dia | Tópico |
|---|---|
| Seg | Espaço |
| Ter | Ilusões de ótica |
| Qua | Física |
| Qui | Como funciona em 3D |
| Sex | Terra e natureza |
| Sáb | Tamanho e escala |
| Dom | Satisfying |

- A produção roda todo dia às 05:47 de Brasília e agenda os vídeos do dia seguinte. Assim sobra 1 dia para o usuário
  ver e cancelar no YouTube Studio.

## 5. Publicação

- **Título:** as 3–4 primeiras palavras dizem o tema e prendem ("What If You Jumped Into Jupiter?"), até 2 emojis no
  fim. O título cumpre o que promete. O padrão de título não se repete em dias seguidos.
- **Descrição:**
  - 1 frase-resumo;
  - a lista do ranking (se houver);
  - a pergunta;
  - 1 linha com 5–6 palavras-chave separadas por vírgula;
  - "Animation: Fun Stuff · Voiceover: AI voice.";
  - `#shorts` + 2–3 hashtags do tema.
- **Tags:** 6–8. **Made for kids: não.**
- O upload sobe privado com `publishAt` horas depois, para o HD ser processado antes de o vídeo ir ao ar.

## 6. Métricas e decisões

- **Painel:** `python3 shorts/metricas.py` gera a tabela por vídeo e o resumo por formato e por tópico (views,
  engajamento, duração média, % assistida). A rotina cola o resultado em `tendencias/AAAA-MM-DD.md` todos os dias.
- **Para que serve cada métrica:**
  - **% assistida** (Analytics, atrasa 2–3 dias): retenção. Meta ≥ 70 %. Abaixo de 50 %, o gancho ou o ritmo falharam.
  - **Engajamento** = (likes + comentários + compartilhamentos) / views. Hoje fica em 1,2–2 %. Meta ≥ 3 %.
  - **Presa na amostra:** mais de 48 h e menos de 300 views. A amostra inicial reprovou: rever o gancho e o tema.
- **Regras de decisão:**
  - **Todo domingo:** reordenar os tópicos do nicho pela tendência + desempenho do canal (a média do canal vale
    metade da nota).
  - Formato abaixo da mediana do canal por 2 semanas sai do rodízio ou é refeito.
  - **08/11:** comparar a semana de 2/dia com a de 3/dia (views por vídeo, % assistida, engajamento) e recomendar ao
    usuário. **O usuário decide.**
  - **15/11:** primeira avaliação do Quark (vídeos com Quark vs. sem). Se for pior, melhorar o roteiro e o gancho
    antes de desistir do mascote.

## 7. Regras para monetizar (e continuar monetizando)

O que mais derruba canais como este na revisão do YPP é **"conteúdo reutilizado"** e **"conteúdo inautêntico"**
(produzido em massa, repetitivo). Por isso:

1. **Nunca usar clipes de outros criadores**, nem de canais concorrentes, TikTok ou "compilações".
2. **No máximo 1 vídeo por dia com cenas de banco de imagens** (Pixabay), sempre com roteiro próprio, dados reais,
   edição, legendas e créditos na descrição. Hoje não usamos nenhuma.
3. **Cada vídeo com subtema, formato e roteiro diferentes.** Nenhum subtema se repete em 30 dias. O título precisa
   cumprir o que promete.
4. **Música:** só original ou sintetizada pelo próprio pipeline. **Nunca** música com direitos autorais. Nem a dica de
   "música viral no volume zero".
5. **IA:** voz de IA não exige aviso. Imagens realistas geradas por IA (pessoas, lugares ou eventos que parecem reais)
   exigem `containsSyntheticMedia: true`. Hoje não usamos nenhuma: o Quark e as cenas são desenho por código.
6. **"Made for kids": não.** O Quark é desenho animado, mas o tom é de ciência para adolescentes e adultos, sem
   linguagem infantil. Ele nunca morre nem se machuca de verdade.
7. **Duração de 20 a 60 s**, gancho no 1º segundo, final que emenda no começo quando der.
8. **Toda semana**, dar mais espaço ao que funciona e tirar o que fica abaixo da média (seção 6).

## 8. Limites técnicos

- **Cota do YouTube:** 10.000 unidades/dia (renova à meia-noite do Pacífico). Cada upload gasta 1.600. 3 uploads
  (4.800) + buscas (~300) + painel de métricas (~10) cabem; no domingo, a medição completa usa ~1.600 a mais.
- **Credenciais:** `YT_CLIENT_ID`, `YT_CLIENT_SECRET` e `YT_REFRESH_TOKEN`, com os escopos `youtube.upload`,
  `youtube.readonly` e `yt-analytics.readonly` (trocado em 31/10). Mudança nas variáveis só vale em sessão/container
  novo.
- **vidIQ:** 150 créditos/mês, 5 por busca, no máximo 1 por dia. A pesquisa principal é pela API do YouTube.
- **Repositório:** os `.mp4` não ficam no Git, só os metadados e o `uploaded.json`.
- **Render:** cairo ~1–2 min por Short; 3D ~4 min (Chromium + SwiftShader). O disco é curto (~4 GB livres): apague os
  `.mp4` de lotes já enviados quando precisar.

## 9. Histórico das decisões

- **25/10:** canal criado; lote 1 de satisfying genérico (fraco).
- **27/10:** formato "tópico em alta + 3 formatos" (passou de 1 mil views).
- **30/10:** formato 3D "como funciona" incluído a pedido do usuário.
- **31/10:**
  - nicho estreitado;
  - mascote Quark criado;
  - teste de 2 vídeos por dia;
  - Analytics ligado;
  - layout ajustado à área segura dos Shorts.
