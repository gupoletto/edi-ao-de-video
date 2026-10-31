# Plano do canal Fun Stuff (@funstuff-67)

Shorts em inglês para público dos EUA, com visual 100% original gerado por código e voz de IA. **Nicho (desde 31/10/2026): ciência visual e simulações satisfatórias.** Os tópicos ficam sempre dentro desse guarda-chuva, para o mesmo espectador, e a escolha segue o que está em alta (veja `TOPICOS.md`). O mascote **Quark** (`pipeline/personagem.py`) é a marca do canal e conta os "what if / why". As lições das referências estão em `ESTRATEGIA.md`.

## Situação em 25/10/2026

- Canal novo: 0 inscritos, 0 vídeos. **Ainda não está no Programa de Parcerias (YPP).**
- Para ganhar com anúncios em Shorts, o YPP exige **1.000 inscritos + 10 milhões de visualizações válidas de Shorts em 90 dias** (ou 4.000 horas de exibição em vídeos longos em 12 meses).
- O objetivo agora é **entrar no YPP e não ser recusado na revisão**. A revisão é feita por uma pessoa, que olha o canal inteiro.

## Agenda de publicação

3 Shorts por dia (**teste de 2 por dia de 02/11 a 08/11**: 12h e 19h em Nova York nos dias úteis, 10h e 19h no fim de semana), sempre um pouco antes dos **picos de audiência do YouTube nos EUA** (horário de Nova York; o `upload.py` ajusta sozinho o horário de verão americano):

| Dia | Horários (Nova York) | Em Brasília (até 31/10) | Em Brasília (a partir de 1/11) |
|---|---|---|---|
| Seg–sex | 12h · 15h · 19h | 13h · 16h · 20h | 14h · 17h · 21h |
| Sáb–dom | 10h · 14h · 19h | 11h · 15h · 20h | 12h · 16h · 21h |

- Os picos são o almoço, a saída da escola ou do trabalho e a noite. No fim de semana, o pico da manhã começa mais cedo.
- **Um tópico por dia da semana**, com vídeos diferentes dele (ranking, "what if/why" com o Quark, interativo ou 3D). O top 10 de tópicos e a agenda da semana ficam em `TOPICOS.md`, atualizados pela rotina conforme o que está em alta.
- A produção roda todo dia de manhã (05:47 em Brasília) e agenda os vídeos nos próximos horários livres, normalmente os do dia seguinte. Assim sempre sobra folga para conferir ou cancelar no YouTube Studio.
- Lote 1 (agendado em 25/10): física dom 25/10 20h · matemática seg 26/10 13h · gelo seg 26/10 20h · fábrica ter 27/10 13h · lava qua 28/10 13h (horários de Brasília).
- Quando houver dados do próprio canal, a rotina ajusta esses horários pelo horário de pico real da audiência.

## Primeira pesquisa (25/10, vidIQ), dentro do nicho "satisfying"

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

**Conclusão:** simulações geradas por código estão em alta e são o tipo mais seguro para a monetização, porque são 100% originais. A pesquisa ampla de tópicos, que define a agenda, está em `TOPICOS.md`.

## Regras para monetizar (e continuar monetizando)

O que mais derruba canais como este na revisão do YPP é **"conteúdo reutilizado"** e **"conteúdo inautêntico"** (produzido em massa, repetitivo). Por isso:

1. **Nunca usar clipes de outros criadores**, nem de canais concorrentes, TikTok ou "compilações". Muitos canais de ranking fazem isso e não são aprovados, ou perdem a monetização depois.
2. **No máximo 1 vídeo por dia com cenas de banco de imagens** (Pixabay; a Pexels suspendeu novas chaves). E sempre com roteiro próprio, dados reais (temperaturas, números), edição, legendas e créditos na descrição.
3. **Cada vídeo com subtema, formato e roteiro diferentes.** Os 3 do dia dividem o tópico, mas nunca o subtema nem o formato. Nenhum subtema se repete em 30 dias, nem o padrão de título em dias seguidos. O título precisa cumprir o que promete.
4. **Música:** só original ou sintetizada pelo próprio pipeline. **Nunca** música com direitos autorais.
5. **IA:** voz de IA não exige aviso. Se algum vídeo tiver imagens realistas geradas por IA (pessoas, lugares ou eventos que parecem reais), marcar `containsSyntheticMedia: true`.
6. **"Made for kids": não.** Descrição curta, sem lista de links: gancho, pergunta para comentários, hashtags `#shorts` + 3 ou 4 do tema.
7. **Duração de 20 a 60 s** (o YouTube aceita Shorts de até 3 min, mas curto retém melhor), gancho no primeiro segundo, final que emenda no começo (loop).
8. **Toda semana**, olhar quais vídeos do canal foram melhor e dar mais espaço aos temas que funcionam. Formato que fica abaixo da média por 2 semanas sai do rodízio.

## Limites técnicos

- **Cota do YouTube:** cada upload gasta 1.600 de 10.000 unidades/dia (renova à meia-noite do horário do Pacífico). 3 uploads (4.800) + 3 buscas diárias (300) cabem; no domingo, o ranking completo usa ~1.600 a mais.
- **vidIQ:** plano gratuito, 150 créditos/mês, 5 por busca. Uso no máximo 1 busca por dia, e a pesquisa principal é feita pela própria API do YouTube.
- **Repositório:** depois do upload, os `.mp4` não ficam no Git. Só os metadados e o `uploaded.json`, para o repositório não crescer ~3 GB por mês.
