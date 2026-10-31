# Top 10 tópicos em alta + agenda da semana

> Arquivo vivo: a rotina diária o atualiza (ranking completo todo domingo; troca no meio da semana se um tópico despencar).
> Última atualização: **25/10/2026**, a partir de 24 tópicos medidos na API do YouTube (Shorts em inglês, publicados de 18 a 25/10, top 25 por views em cada busca).

## Ranking atual

A posição pesa a **mediana de views** (mais confiável que a soma, que um único viral distorce), o ritmo de views/hora, se dá para produzir com **visual 100% original** (sem imagens de terceiros) e se o tema é seguro para monetização.

| # | Tópico | Mediana de views (7 dias) | Exemplos em alta | Formato original possível |
|---|---|---:|---|---|
| 1 | **História "What if" e impérios** | 290 mil | "If empires had sound" (3,2 mi), "What if you were painted centuries ago?" | Mapas animados, linhas do tempo, impérios crescendo |
| 2 | **Ilusões de ótica** | 376 mil | "Do you think it's a giant or just a visual illusion?" (1,8 mi) | 100% gerável por código: ilusões clássicas e novas |
| 3 | **Espaço** | 111 mil | "Why nothing can survive Venus" (1,6 mi), "What if a coin-sized black hole appeared?" (677 mil) | Simulações de órbitas, planetas, buracos negros |
| 4 | **Simulações de física** | 358 mil* | "Bouncing emoji balls multiply in a spiral!" (3,2 mi) | O que o canal já faz: bolinhas, caos, pêndulos |
| 5 | **Países e geografia ranqueados** | 208 mil | "Countries ranked by their first letter" (643 mil), "What if Russia moved to Canada?" | Mapas, bandeiras, gráficos de dados reais |
| 6 | **Dinossauros e Terra pré-histórica** | 1,6 mi* | "Welcome to Earth 210 million years ago" (4,5 mi) | Comparação de tamanho, Terra mudando ao longo das eras |
| 7 | **Mitologia e civilizações antigas** | 578 mil* | "The clever survival trick used during ancient Chinese wars" (1,5 mi) | Deuses ranqueados, maravilhas antigas, mapas |
| 8 | *Reserva:* Rankings "satisfying" | 132 mil | "Ranking the most satisfying vids" (1,2 mi) | Simulações satisfying (estilo do lote 1) |
| 9 | *Reserva:* Comparação de tamanho | 165 mil | "Big vs. small! A fun size guessing game" | Escala de animais, prédios, planetas |
| 10 | *Reserva:* Ciência da comida e "did you know" | 97–192 mil | "Why do Mongolians eat meat 3 times a day?" | Infográficos animados |

\* Mediana inflada por virais fora do tema (desenho infantil, vídeos em outras línguas). O tópico continua forte, mas foi posto abaixo do que os números brutos sugerem.

Ficaram de fora (fracos ou inviáveis sem imagens reais): tecnologia/IA, física do esporte, comparação de carros, ranking de animais, engenharia, dinheiro, desastres naturais, fundo do mar.

## Agenda da semana (a partir de 26/10)

Cada dia tem **um tópico**, com **3 vídeos diferentes** dele, um em cada horário de pico:

| Dia | Tópico |
|---|---|
| Segunda | 1 · História "What if" e impérios |
| Terça | 2 · Ilusões de ótica |
| Quarta | 3 · Espaço |
| Quinta | 4 · Simulações de física |
| Sexta | 5 · Países e geografia ranqueados |
| Sábado | ~~6 · Dinossauros e Terra pré-histórica~~ → 9 · Comparação de tamanho (troca em 30/10: dinossauros caiu para 40 mil de mediana; tamanho está em 130 mil) |
| Domingo | ~~7 · Mitologia e civilizações antigas~~ → 8 · Satisfying rankings (troca em 31/10: mitologia ficou entre 11 e 21 mil de mediana; satisfying está em 153 mil) |

Durante a transição (até 28/10), alguns horários já estão ocupados por vídeos do lote 1 (gelo, fábrica e lava). Nesses dias, a rotina produz só o número de vídeos que cabe nos horários livres.

## Os 3 vídeos do dia: sempre diferentes entre si

Os três são do mesmo tópico, mas com **subtema e formato diferentes**:

1. **Ranking** (#5 → #1), no estilo do lote 1. Ex.: "Ranking the largest empires in history".
2. **"What if / Why"**: explicação com simulação. Ex.: "What if the Roman Empire never fell?"
3. **Interativo**: quiz, "can you spot it?", "guess which…". Ex.: "Guess the empire from its map".

Nenhum subtema se repete em 30 dias (controle em `historico.md`). O padrão de título também não se repete em dias seguidos.

## Cuidados por tópico

- **Dinossauros:** tom científico, não infantil. Conteúdo com cara de "para crianças" pode ser marcado como *made for kids*, o que corta anúncios e comentários.
- **Mitologia:** só mitologias antigas (grega, nórdica, egípcia, mesopotâmica, asteca). Nada de religiões praticadas hoje.
- **História e países:** nada de conflitos atuais ou temas políticos sensíveis. Fatos e números conferidos.
- **Ilusões de ótica:** as clássicas são domínio público como ideia, mas a arte precisa ser gerada pelo nosso código.

## Como o ranking é atualizado

- **Todo domingo:** a rotina mede de novo os 10 tópicos e mais 5 candidatos novos (temas que aparecerem nas buscas da semana), reordena o top 10 e refaz a agenda da semana seguinte.
- **Todo dia:** 1 a 3 buscas dentro do tópico de amanhã, para achar os subtemas e formatos que estão subindo agora.
- **Troca no meio da semana:** se um tópico da agenda cair pela metade e uma reserva estiver bem acima, a reserva entra no lugar dele.
- **Dados do próprio canal:** depois de 2 semanas de vídeos, a média de views do Fun Stuff em cada tópico passa a valer metade da nota.
