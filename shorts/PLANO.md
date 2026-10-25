# Plano do canal Fun Stuff (@funstuff-67)

Shorts em inglês para público dos EUA, no formato "Ranking the most satisfying …" com voz de IA.

## Situação em 25/10/2026

- Canal novo: 0 inscritos, 0 vídeos. **Ainda não está no Programa de Parcerias (YPP).**
- Para ganhar com anúncios em Shorts, o YPP exige **1.000 inscritos + 10 milhões de visualizações válidas de Shorts em 90 dias** (ou 4.000 horas de exibição em vídeos longos em 12 meses).
- O objetivo agora é **entrar no YPP e não ser recusado na revisão**. A revisão é feita por uma pessoa, que olha o canal inteiro.

## Agenda de publicação

3 Shorts por dia, todos os dias, nestes horários (UTC):

| Horário UTC | Brasília | Nova York (EDT) | Tipo de vídeo |
|---|---|---|---|
| 15:00 | 12h | 11h | **A — simulação original** (física, caos, bolinhas, "will it escape?") |
| 19:00 | 16h | 15h | **B — tema em alta** (ranking com cenas do Pexels, roteiro e dados próprios) |
| 23:00 | 20h | 19h | **C — matemática/visual original** ou quiz ("wait for #1", "guess which…") |

- A produção roda todo dia de manhã (05:47 em Brasília) e já agenda os vídeos do **dia seguinte**. Assim sempre sobra um dia de folga: se algo falhar, nenhum horário fica vazio, e você pode conferir ou cancelar no YouTube Studio antes de o vídeo ir ao ar.
- O lote 1 (os 5 vídeos já prontos) sai às 19:00 UTC, de 26/10 a 30/10.

## O que está em alta (pesquisa de 25/10 no vidIQ)

Formatos "Ranking …" estourando em canais pequenos nas últimas 2 semanas:

- **Lava/vulcão** (1,6 mi de views em canal de 6 mil inscritos)
- **Quebra de gelo** (1,5 mi em canal de 3,9 mil)
- **Máquinas de fábrica** (1,6 mi)
- **"Physics moments"** (4,8 mi em canal de 4,6 mil)
- **Experimentos que parecem mágica** (10,9 mi)
- **Simulação de bolinha em espiral** (3,8 mi em canal de 2,5 mil, 100% gerada por computador)
- **Objetos impressos em 3D** (19,7 mi)
- **Construção** (850 mil)
- **Mentos + Coca** (340 mil)

**Conclusão:** simulações de física geradas por código estão em alta e são o tipo mais seguro para a monetização, porque são 100% originais. Por isso elas ficam com o horário A, todos os dias.

## Regras para monetizar (e continuar monetizando)

O que mais derruba canais como este na revisão do YPP é **"conteúdo reutilizado"** e **"conteúdo inautêntico"** (produzido em massa, repetitivo). Por isso:

1. **Nunca usar clipes de outros criadores**, nem de canais concorrentes, TikTok ou "compilações". Muitos canais de ranking fazem isso e não são aprovados, ou perdem a monetização depois.
2. **No máximo 1 vídeo por dia com cenas de banco de imagens** (Pexels). E sempre com roteiro próprio, dados reais (temperaturas, números), edição, legendas e créditos na descrição.
3. **Cada vídeo com tema e roteiro diferentes.** Nada de repetir o mesmo tema em menos de 14 dias, nem o mesmo padrão de título dois dias seguidos. O título precisa cumprir o que promete.
4. **Música:** só original ou sintetizada pelo próprio pipeline. **Nunca** música com direitos autorais.
5. **IA:** voz de IA não exige aviso. Se algum vídeo tiver imagens realistas geradas por IA (pessoas, lugares ou eventos que parecem reais), marcar `containsSyntheticMedia: true`.
6. **"Made for kids": não.** Descrição com créditos, hashtags `#shorts` + 3 ou 4 do tema.
7. **Duração de 20 a 60 s**, gancho no primeiro segundo, final que emenda no começo (loop).
8. **Toda semana**, olhar quais vídeos do canal foram melhor e dar mais espaço aos temas que funcionam. Formato que fica abaixo da média por 2 semanas sai do rodízio.

## Limites técnicos

- **Cota do YouTube:** cada upload gasta 1.600 de 10.000 unidades/dia. 3 uploads (4.800) + até 10 buscas de tendência (1.000) cabem com folga.
- **vidIQ:** plano gratuito, 150 créditos/mês, 5 por busca. Uso no máximo 1 busca por dia, e a pesquisa principal é feita pela própria API do YouTube.
- **Repositório:** depois do upload, os `.mp4` não ficam no Git. Só os metadados e o `uploaded.json`, para o repositório não crescer ~3 GB por mês.
