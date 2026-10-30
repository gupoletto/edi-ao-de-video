# Guia de estilo da edição pessoal

Aprendido de cinco vídeos de referência (análise quadro a quadro, transcrição e medição do áudio, em 28/10/2026):

- **A — Marcos Lemos**, "Como editar vídeos com IA usando o Claude Code (passo a passo)", 16:56, 1080p. Editado por IA.
- **B — Matheus Fonseca**, "Como Eu Crio e Edito Meus Vídeos com o Claude Opus 5.5", 8:02.
- **C — Léo Lamera**, "O jeito certo de editar vídeo com o Claude (processo completo)", 15:38.
- **D — Felipe Borges**, "Isso transforma o Claude em um gênio da edição de vídeo por R$0", 21:11.
- **E — LABS**, "Fiz 60 vídeos com Claude sem editar", 10:48 (motion graphics em massa para Reels).

Este arquivo é o "guia de estilo" que o vídeo A manda criar: o Claude lê antes de planejar cada vídeo.
Edite à vontade (cores, fontes, o que você não quer) e coloque referências visuais em `edicao/estilo/`.

## 0. Paleta do canal (vale para todos os estilos; definida em 28/10/2026)

| Cor | Hex | Uso |
|---|---|---|
| Marinho | `#01103A` | fundo dos cards de tela cheia, pílulas sobre o vídeo, contorno das legendas |
| Creme | `#F8EDD9` | texto principal e legendas |
| Taupe | `#B19F92` | destaque: a palavra em cor do título, números, palavra-chave da legenda, item "não" |
| Cinza-azulado | `#919FA8` | secundário: rótulos, itens já feitos/apagados, item "ok" |

Regra: texto sempre creme sobre marinho (ou sobre o vídeo). Taupe e cinza-azulado só sobre fundo escuro —
sobre o creme eles não têm contraste. Fica em `PALETA` no `ferramentas/elementos.py`. As cores das seções 2 e 3
(creme do Marcos, branco do Matheus) descrevem as referências; o kit usa esta paleta.

## 1. Ritmo (vale para os dois estilos)

| Medida | A | B | C | D | E | Regra no editor |
|---|---|---|---|---|---|---|
| Fala ocupando o vídeo | 97 % | 89 % | 98 % | 95 % | 99 % | cortar toda pausa > 0,35 s (`--ritmo rapido`: 0,25 s) |
| Pausa típica entre frases | 0,27 s | 0,27 s | 0,24 s | 0,37 s | 0,22 s | deixar 0,1 s de respiro de cada lado |
| Pausas > 0,6 s no vídeo todo | 7 | 5 | 0 | 26 | 2 | quase nenhuma |
| Velocidade da fala | 176 | 184 | 231 | 244 | 221 palavras/min | — (é como você fala) |
| Troca de plano | ~6 s | ~5,5 s | ~1–3 s | ~6 s | ~1,7 s | um elemento ou zoom a cada 2–8 s (mais rápido em Reels) |

- **Corte seco** (jump cut) entre frases, sempre no silêncio, nunca no meio de palavra.
- **Regravações saem**: se você repetiu a frase, fica a última tomada.
- **Gancho nos primeiros 3–20 s**, com o rosto: o que o vídeo entrega + por que confiar ("tudo que você está vendo foi editado por IA",
  "eu fiz esses 60 vídeos em 30 minutos"). C e E abrem com um número grande ou com o resultado antes de qualquer explicação.
- **A abertura se faz por último** (C): depois de editar tudo, escolha 2–3 trechos fortes do próprio vídeo e ponha na frente
  (`"abertura"` no plano). C fez uma abertura de 1:52 com 120 mídias.
- **Mapa logo no começo** (A, aos 2:02: "o processo tem 6 etapas") e **resumo no final** (A, 15:00).
- Final: pedido de comentário + inscrição, sem enrolar.

## 2. Estilo "editorial" (A) — `--estilo editorial`

Inspirado nas janelas do próprio Claude: limpo, papel creme, serifa.

- **Fundo** creme `#F4F2EC`; **texto** quase preto `#1F1E1D`; **destaque** terracota `#C96442`; ok verde, erro vermelho.
- **Título** em serifa (Source Serif 4 Semibold) no alto à esquerda, com **uma ou duas palavras em terracota**:
  "Só o arquivo e as **instruções**", "Você **não precisa**", "Dois **caminhos**", "Quem faz **o quê**".
- **Corpo** em sans bold (Inter). Cartões brancos com cantos arredondados e sombra leve.
- **Cards de etapa**: "PASSO 2 DE 5" pequeno em terracota + título grande centralizado + traço curto embaixo.
- **Listas** que entram item a item, com ✓ verde ou ✗ vermelho (o ✗ às vezes risca o item).
- **Letreiros sobre o rosto**: pílulas brancas empilhadas no canto, entrando uma a uma ("Cada corte", "Cada animação", "Cada letreiro").
- **Tela dividida**: rosto à esquerda (~1/4) e painel creme à direita com o conteúdo.
- **Sem legendas** contínuas (o texto vem dos cards). Transição: entrada rápida (fade + subida de ~20 px), nada girando.
- Telas de programas são **recriadas** como ilustração (janela simplificada), não gravação de tela crua.

## 3. Estilo "dinâmico" (B) — `--estilo dinamico`

Mais rápido, feito para vertical (Reels/TikTok/Shorts) e para tutoriais com gravação de tela.

- **Rosto em tela cheia** no gancho; depois **gravação de tela com a câmera em miniatura** no canto inferior esquerdo.
- **Explicadores em tela branca** `#FAFAFA` com **selo numerado** vermelho (①②③) e elementos que surgem um a um (barra de prompt digitando, miniaturas, setas).
- **Legendas palavra a palavra**: 1–3 palavras, sans pesada branca (Poppins ExtraBold) com contorno preto, no terço inferior;
  a **palavra-chave em itálico amarelo** ("inteiramente", "vídeo", "resto"). Entram com um "pulo" curto.
- Cards de título com tipografia grande e texto "sendo digitado" (cursor), fundo escuro texturizado.
- Música/efeitos sincronizados com as batidas nos trechos de motion graphic.

## 3b. Estilo "frase-chave" (C, Léo Lamera) — `"legenda_estilo": "frase"`

- Rosto em tela cheia, fundo escuro e quente. **Legenda de 2–3 palavras** no centro de baixo: sans pesada branca
  (Poppins ExtraBold) e **a palavra mais importante em serifa itálica clara** ("direto ao *ponto*", "todo o meu *processo*").
  Entra desfocada e foca em ~0,15 s.
- **Rosto num cartão arredondado** à esquerda, texto grande à direita em fundo branco/creme (`dividido`).
- Etiquetas brancas flutuando em volta do rosto ("testar", "e baixar"), palavra **riscada** ("~genérico~").
- **Sumário** do vídeo com a etapa atual em destaque e as anteriores marcadas (`sumario`).
- **Contadores** que sobem até o número ("R$ 0 → R$ 1", "11.355 palavras") (`numero` com `contar_de`).
- Fotos/reportagens com o rosto em **miniatura redonda** no canto; uma faixa de cores no rodapé como marca.

## 3c. Tutorial com tela (D, Felipe Borges) — elemento `tela`

- **Gravação de tela em tela cheia + rosto em miniatura** de cantos arredondados num canto livre.
- O motion graphic deixa **o primeiro terço da tela vazio** para o rosto; quando a animação muda de lado, **a miniatura
  muda de lado** junto (dois elementos `tela` seguidos com `pip` diferente).
- **Holofote** (`foco`): escurece tudo fora de uma área para apontar um detalhe; **pop-up** (`popup`): recorta a área e
  mostra ampliada na frente.
- Thumbnail com o **texto atrás da pessoa** (recorte do fundo) — ainda não automatizado aqui.

## 3d. Motion graphics para Reels (E, LABS)

- Abertura com **números gigantes** ("60 vídeos — 30 minutos") sobre uma grade de vídeos; ícones dos editores **riscados**.
- Cards "**Passo 1**" com moldura e subtítulo em serifa itálica; logos ligados por uma linha (fluxo A → B).
- Selo "**Link na descrição**" pequeno no canto inferior, cor forte (magenta).
- Método: estudar um vídeo de referência quadro a quadro, **testar com um trecho de ~12 s**, só então fazer o resto;
  depois **transformar o processo numa skill**. Efeitos sonoros e b-roll numa pasta que o Claude consulta.

## 3e. Fugindo do óbvio (criado no episódio 10, 29/10/2026)

As referências abrem com o resultado ou um número. Num vlog com história, funciona melhor:
- **Abrir no conflito** (o momento de maior tensão do próprio vídeo, mesmo que seja do fim do dia) e voltar no tempo
  com um selo discreto ("17 horas antes") em vez de um card de "flashback".
- **Relógio do dia**: um `selo` fixo no canto que muda por fase ("Dia 10/30 · manhã" → "noite" → "quase meia-noite").
- **Progresso da série** (`progresso`) na abertura e no fecho: 30 blocos, o de hoje acende por último; o fecho
  promete o próximo ("Amanhã: dia 11").
- **Plano vs. realidade**: o plano dito de manhã vira um `dividido` com itens no tempo da fala; à noite, uma `lista`
  com o que deu certo e o que ficou riscado. A edição conta a história por *callback*.
- ~~**Match cut** com a camiseta depois do tapa~~: o usuário pediu para tirar (tapa = fim do take, seção 5).
- **Transições temáticas** (`transicao`, pedido do usuário no episódio 10) em cada troca de lugar ou de hora, cada uma
  contando algo da história e cobrindo a tela no corte:
  - `roda`: saída de bike;
  - `rota`: mapa do dia com paradas, e o ponto anda até a próxima; é o fio que amarra o vlog, então use a mesma
    lista de `paradas` no vídeo todo;
  - `relogio`: salto de horas no mesmo lugar;
  - `cortina` com texto: antes do evento;
  - `flash`: entrada no show ou na festa.
  Outros estilos (cada um com o seu som, em `sons.DA_TRANSICAO`):
  - `blocos`: pixels em onda; rotina ou tecnologia;
  - `tinta`: respingo; virada de humor;
  - `glitch` com `texto`: algo deu errado, ou um "DIA 11";
  - `papel` com `texto`: "enquanto isso...";
  - `iris`: fecha no rosto, para uma piada ou reação;
  - `persiana`: troca de ambiente dentro de casa;
  - `filme` 3-2-1: flashback, ou "vamos lá";
  - `celular`: alarme, mensagem ou lembrete que muda o dia, com a notificação escrita;
  - `polaroid` com legenda: um momento para guardar, ou uma foto do lugar.
  - Criados no episódio 11:
    - `cronometro`: relógio de corrida com km e pace;
    - `cupom`: o que foi comprado, com "total" de brincadeira;
    - `anilhas`: entrada na academia;
    - `vapor`: o prato pronto;
    - `rebobinar`: VHS do gancho de volta para o começo do dia.
    Prefira inventar uma transição que nasça do assunto do dia a repetir a do episódio anterior.
  Uma a cada troca de cena, nunca em corte de pausa. Varie o estilo e não use mais de ~8 por vídeo. A cena nova
  deve começar no rosto ou na ação: corte antes o pedaço em que a câmera ainda está virando (camiseta, chão).
- **Momento cinema**: no trecho mais visual, faixas de cinema (`foco` com `contorno: false`) e o som abafado.
- **Música de terceiros** (show, bar, carro): mostre poucos segundos e use `abafar`; o Content ID do YouTube ainda
  pode reconhecer, então avise antes de publicar.

## 3g. Vidro, menos azul chapado (pedido do usuário, episódio 11 refeito)

- `"vidro": true` (padrão): nos cards de tela cheia e nas transições, o marinho chapado vira véu de cerca de 40 % sobre o
  próprio vídeo desfocado (gblur). Em volta dos textos e ícones o marinho volta num degradê, para manter a leitura.
  Pílulas e selos ficam com cerca de 70 %.
- As transições são 1,4x mais longas que a primeira versão. O desfoque cresce até o corte e some depois, então o corte
  some no vidro sem precisar de uma tela sólida.
- Objetos (anilha, relógio, cupom, polaroid, papel) continuam opacos: são "coisas" na cena, não fundo.

## 3f. Trilha e vinheta (pedido do usuário, 29/10/2026)

- **Trilha** sempre ligada, para o vídeo não ficar "seco", e sempre sintetizada (`sons.py`), nunca música baixada:
  - `lofi` para o dia a dia;
  - `pop` para montagem rápida, treino ou correria;
  - `chill` para fala longa e reflexão;
  - `epico` para a chegada, a conquista ou o show.
  Troque o estilo por trechos quando o clima muda. Volume 0,25–0,35: a voz tem que vencer sempre. No trecho com
  música de terceiros (show), não ponha trilha.
- **Vinheta de fim** em todo vídeo (`"vinheta": true`): ela pede inscrição, like e o comentário "o que você quer ver
  nos próximos vídeos?", e deixa 6,5 s para a tela final do YouTube.

- **Thumbnail**: cada episódio com um conceito novo, nunca o mesmo layout. Já usados: episódio 10, recorte com
  contorno, ingresso e carimbo (`thumb.py --recortar --bilhete`); episódio 11, HUD de videogame "NÍVEL 11" com XP e
  conquistas (`thumb_jogo.py`). Use um quadro em que o usuário esteja sorrindo e bem iluminado.

## 4. Quando usar cada elemento (regra para o plano)

| Na fala... | Elemento |
|---|---|
| anuncia uma etapa ("o segundo passo...") | `titulo` com `rotulo: "PASSO N DE M"` |
| enumera 3+ coisas, ou "você não precisa de X, Y" | `lista` (`marca`: check, x ou numero) |
| diz um número que importa (preço, tempo, %) | `numero` |
| lista rápida de 2–4 palavras enquanto fala para a câmera | `letreiro` |
| frase de efeito / ênfase | zoom no rosto (já automático a cada corte) |
| ideia central explicada com calma (5–8 s) | `dividido` (rosto no cartão + título e 2–3 tópicos) |
| "primeiro... segundo... por último..." no começo | `sumario` com `atual: 0`; repita com `atual` maior a cada etapa |
| mostra algo no computador / celular | `tela` (a gravação vai em `bruto/`), `pip` do lado livre |
| "olha esse detalhe aqui" | `foco` ou `popup` com a `area` |
| "não é X" / "esqueça X" | `letreiro` com `"~X~"` |

**Leia a transcrição como o "cérebro" do vídeo (C):** marque pessoas, objetos, números e datas citados — cada um é
candidato a um elemento. Escreva antes um **roteiro de edição** (o que aparece na tela em cada frase) e só depois
preencha `elementos`.

- No máximo **um elemento a cada 5 s**; deixe o rosto aparecer pelo menos 3 s entre elementos de tela cheia.
- Textos curtos: título ≤ 6 palavras, item de lista ≤ 5 palavras.
- **O que não fazer**: emoji nos cards, transição girando, texto que só repete a fala inteira, mais de 2 cores de destaque.

## 5. Revisão antes do final (vídeo A, 13:40)

1. Ver a **amostra dos 3 primeiros elementos** (`elementos.py --amostra`) antes de renderizar todos.
2. Aprovar o estilo num **trecho de ~1 min** (`montar.py --previa --trecho 60 120`) — o feedback aprovado vira regra
   neste arquivo — e só então assistir à **prévia inteira**.
3. Conferir **todo texto na tela** (erro de digitação) e nomes na transcrição (ex.: "cloud" → "Claude" em `correcoes`).
4. Ouvir o áudio: **nenhum corte no meio de palavra**.
4c. **Pé, chão ou cama no começo e no fim do take** (regra do usuário, episódio 11): o `tapas.py` tira as pontas sem
   rosto dos clipes em que você fala. Se um clipe inteiro mostra só a cama ou o chão enquanto você fala, cubra com um
   card de tela cheia que ilustre a fala (no episódio 11, a `lista` "Antes do trampo").
4b. **Tapa na câmera = fim do take.** Nada depois do tapa aparece (camiseta, chão, câmera balançando), nem num
   efeito criativo: no episódio 10 a camiseta do Eddie depois do tapa virou um match cut e o usuário pediu para tirar.
   O `montar.py` já aplica isso sozinho; confira na lista "tirado ... (tapa na câmera)" que ele imprime.
5. Final para YouTube: 1920×1080 (ou 1080×1920 vertical), fps do original, H.264 + AAC, −14 LUFS.
6. Quer o último ajuste à mão? `exportar.py` gera um EDL para abrir no Premiere, DaVinci ou Final Cut (A e C fazem isso).
