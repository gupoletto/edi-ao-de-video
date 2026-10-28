# Guia de estilo da edição pessoal

Aprendido de dois vídeos de referência (análise quadro a quadro, transcrição e medição do áudio, em 28/10/2026):

- **A — Marcos Lemos**, "Como editar vídeos com IA usando o Claude Code (passo a passo)", 16:56, 1080p. Editado por IA.
- **B — Matheus Fonseca**, "Como Eu Crio e Edito Meus Vídeos com o Claude Opus 5.5", 8:02.

Este arquivo é o "guia de estilo" que o vídeo A manda criar: o Claude lê antes de planejar cada vídeo.
Edite à vontade (cores, fontes, o que você não quer) e coloque referências visuais em `edicao/estilo/`.

## 1. Ritmo (vale para os dois estilos)

| Medida | A | B | Regra no editor |
|---|---|---|---|
| Fala ocupando o vídeo | 97 % | 89 % | cortar toda pausa > 0,35 s |
| Pausa típica entre frases | 0,27 s | 0,27 s | deixar 0,1 s de respiro de cada lado |
| Pausas > 0,6 s no vídeo todo | 7 | 5 | quase nenhuma |
| Velocidade da fala | 176 palavras/min | 184 palavras/min | — (é como você fala) |
| Troca de plano | a cada ~6 s | a cada ~5,5 s | um elemento ou zoom a cada 5–8 s |

- **Corte seco** (jump cut) entre frases, sempre no silêncio, nunca no meio de palavra.
- **Regravações saem**: se você repetiu a frase, fica a última tomada.
- **Gancho nos primeiros 10–20 s**, com o rosto: o que o vídeo entrega + por que confiar ("tudo que você está vendo foi editado por IA").
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

## 4. Quando usar cada elemento (regra para o plano)

| Na fala... | Elemento |
|---|---|
| anuncia uma etapa ("o segundo passo...") | `titulo` com `rotulo: "PASSO N DE M"` |
| enumera 3+ coisas, ou "você não precisa de X, Y" | `lista` (`marca`: check, x ou numero) |
| diz um número que importa (preço, tempo, %) | `numero` |
| lista rápida de 2–4 palavras enquanto fala para a câmera | `letreiro` |
| frase de efeito / ênfase | zoom no rosto (já automático a cada corte) |

- No máximo **um elemento a cada 5 s**; deixe o rosto aparecer pelo menos 3 s entre elementos de tela cheia.
- Textos curtos: título ≤ 6 palavras, item de lista ≤ 5 palavras.
- **O que não fazer**: emoji nos cards, transição girando, texto que só repete a fala inteira, mais de 2 cores de destaque.

## 5. Revisão antes do final (vídeo A, 13:40)

1. Ver a **amostra dos 3 primeiros elementos** (`elementos.py --amostra`) antes de renderizar todos.
2. Assistir a **prévia inteira** pelo menos uma vez.
3. Conferir **todo texto na tela** (erro de digitação) e nomes na transcrição (ex.: "cloud" → "Claude" em `correcoes`).
4. Ouvir o áudio: **nenhum corte no meio de palavra**.
5. Final para YouTube: 1920×1080 (ou 1080×1920 vertical), fps do original, H.264 + AAC, −14 LUFS.
