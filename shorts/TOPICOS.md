# Top 10 tópicos em alta + agenda da semana

> Arquivo vivo: a rotina diária o atualiza (ranking completo todo domingo; troca no meio da semana se um tópico despencar).
> Última atualização: **31/10/2026**: nicho estreitado (ver abaixo). A medição original de 25/10 cobriu 24 tópicos.

## Nicho do canal (decidido em 31/10/2026): **ciência visual e simulações satisfatórias**

O algoritmo testa cada vídeo com uma amostra de ~200 pessoas parecidas com quem já gostou do canal (`ESTRATEGIA.md`,
seções 7 e 8). Tópicos espalhados confundem essa amostra. Por isso todos os tópicos ficam sob um guarda-chuva só, para
o mesmo espectador: curioso por ciência, que gosta de ver a coisa acontecer na tela.

- **Dentro:** ilusões de ótica, espaço, simulações de física, "como funciona" em 3D (mecanismos), Terra e natureza em
  simulação (vulcões, terremotos, oceanos, clima), comparação de tamanho e escala, satisfying (loops, encaixes,
  simulações).
- **Fora (mesmo se estiverem em alta):** história e impérios, mitologia, dinossauros, países ranqueados por dado
  político ou cultural, comida, celebridades, esporte. Mapas só entram como ciência de escala (ex.: projeção de
  Mercator, tamanho real).
- Candidatos novos no ranking de domingo só se couberem no guarda-chuva.

## Ranking atual (medido em 25–31/10; o domingo reordena só dentro do nicho)

| # | Tópico | Mediana de views (7 dias) | Desempenho no canal | Formato original possível |
|---|---|---:|---|---|
| 1 | **Ilusões de ótica** | 376 mil | 1.256 / 1.040 | Ilusões geradas por código |
| 2 | **Simulações de física** | 358 mil | 925–1.228 | Integração numérica de verdade |
| 3 | **Espaço** | 111 mil | 650–1.182 | Órbitas, planetas, escalas |
| 4 | **Satisfying** (loops, encaixes, enchimento) | 153 mil | (01/11) | `pipeline/satisfying.py` |
| 5 | **Comparação de tamanho e escala** | 130 mil | (31/10) | Escala real, contornos reais |
| 6 | **Como funciona em 3D** (cinematográfico) | **1 mi** em "how it works 3d animation" (31/10) | (01/11) | three.js (`pipeline/tres.py`, `cenas3d/`) |
| 7 | **Terra e natureza em simulação** | a medir no domingo 08/11 | — | Vulcões, placas, ondas, clima |

## Agenda da semana (a partir de 02/11)

**Teste de 2 vídeos por dia, de 02/11 a 08/11** (aprovado em 31/10; os horários estão no `upload.py`):
- **Vídeo A** (12h em Nova York): o tópico do dia, alternando o formato entre Quark what-if, ranking e interativo.
- **Vídeo B** (19h em Nova York): **3D cinematográfico** (formato fixo desde 31/10, a pedido do usuário). O tema vem
  da fila abaixo, sempre dentro do nicho, e não precisa ser o tópico do dia.

| Dia | Tópico do dia | Vídeo A (12h NY) | Vídeo B (19h NY), 3D cinematográfico |
|---|---|---|---|
| Seg 02/11 | Espaço | 3D: como o foguete chega à órbita (B trocado com A neste dia) | Quark: pular em Júpiter ✅ agendado |
| Ter 03/11 | Ilusões de ótica | Interativo | E se o cabo do elevador arrebentar? |
| Qua 04/11 | Simulações de física | Quark what-if | Carro × árvore a 30 mph ✅ pronto (`lote-2026-11-04`) |
| Qui 05/11 | Como funciona | Ranking | Turbina de avião ✅ pronta (`lote-2026-11-05`) |
| Sex 06/11 | Terra e natureza | Interativo | Como o helicóptero voa |
| Sáb 07/11 | Tamanho e escala | Ranking | Como o trem de pouso funciona |
| Dom 08/11 | Satisfying | Quark what-if | Como a eletricidade chega à tomada |

No domingo 08/11 a rotina compara a semana de 2/dia com a semana anterior (3/dia), olhando a média de views por vídeo,
a taxa de engajamento, a % assistida e o desempenho do 3D cinematográfico contra os outros formatos. Ela registra o
resultado em `tendencias/` e no relatório, e recomenda ao usuário: manter 2, voltar para 3 ou testar 1. **Quem decide
é o usuário.** Até ele decidir, o `upload.py` volta sozinho para 3 slots a partir de 09/11.

## Fila do 3D cinematográfico

Pesquisa de 31/10 (`pesquisa.py`, Shorts em inglês dos últimos 30 dias): a busca **"how it works 3d animation"** tem
mediana de **1 milhão** de views. Os maiores são objetos do dia a dia ("How Electrical Outlets Work" 5,7 mi,
"mechanical typewriter" 4,8 mi), veículos e cenários de "o que acontece se" ("What Happens If an Elevator Cable
Snaps?" 1,85 mi; "Why Doesn't Lightning Bring Down an Airliner?" 855 mil). Nossa versão: **cenário real primeiro**
(o avião no céu, o carro na estrada), a câmera entra, o mecanismo é mostrado por dentro (corte, câmera lenta ou
raio-x), a câmera volta e o Quark faz a pergunta.

| # | Tema | Demanda medida | Cenário de abertura → mecanismo |
|---|---|---|---|
| 1 | Como o foguete chega à órbita (vai de lado) | foguetes 53 mil; "why rockets go sideways" 490 mil | Base de lançamento → subida, separação dos estágios, curva para a órbita |
| 2 | E se o cabo do elevador arrebentar? | 1 vídeo com 1,85 mi | Prédio à noite → poço do elevador, cabo arrebenta, freio de segurança trava nos trilhos |
| 3 | Como o helicóptero voa | mediana 207 mil | Helicóptero sobre a cidade → cabeça do rotor (prato oscilante), rotor de cauda |
| 4 | Como o trem de pouso funciona | 1 vídeo com 832 mil | Avião na aproximação → hidráulica abrindo as portas e baixando o trem |
| 5 | Como a eletricidade chega à tomada | 1 vídeo com 5,7 mi | Casa à noite → fiação na parede, fase/neutro/terra, disjuntor |
| 6 | Turbo do carro | 445 mil e 908 mil | Carro acelerando → turbina do escape girando o compressor da admissão |
| 7 | Por que o raio não derruba o avião | 855 mil | Tempestade → raio entra na fuselagem e sai pela cauda (gaiola de Faraday) |
| 8 | Como o submarino mergulha | mediana 58 mil | Superfície do mar → tanques de lastro enchendo, mergulho |
| 9 | Prédio contra terremoto (isolamento de base) | mediana 22 mil; vídeos de 345 mil | Cidade → terremoto, prédio comum × prédio sobre isoladores |
| 10 | Como a descarga do vaso funciona (sifão) | mediana 20 mil; encanamento 136 mil | Banheiro → caixa acoplada, sifão, ventilação |
| 11 | Freio ABS em pista molhada | a medir | Carro freando na chuva → roda travando × ABS pulsando |
| 12 | Máquina de escrever mecânica | 4,8 mi | Escritório antigo → tecla, alavanca, tipo batendo na fita |

**Medidos e fracos agora** (não entram por enquanto): vulcão em 3D (mediana 1,7 mil), dentro do tornado (1,9 mil),
geladeira (5,5 mil), reator nuclear (6,5 mil), represa (9,9 mil). **Fora do nicho e das regras:** armas e mísseis
(estão em alta, mas não fazemos), medicina e anestesia (risco de desinformação).

## Os vídeos do dia: sempre diferentes entre si

São do mesmo tópico, mas cada um tem **subtema e formato diferentes**. O catálogo de formatos (ranking, what if/why com o
Quark, interativo, 3D) e as receitas estão no `PLANO.md`, seção 3. Todo vídeo termina com o Quark fazendo a pergunta
final. Nenhum subtema se repete em 30 dias (controle em `historico.md`), nem o padrão de título em dias seguidos.

## Cuidados por tópico

- **Mascote:** o personagem é desenho animado, mas o tom do roteiro é de ciência para adolescentes e adultos (piadas
  secas, números reais), nunca infantil. Conteúdo com cara de "para crianças" pode ser marcado como *made for kids*,
  o que corta anúncios e comentários. O mascote nunca morre nem se machuca de verdade: o perigo é mostrado com humor
  e ele sempre escapa.
- **Terra e natureza:** desastres sem vítimas reais nem eventos recentes com mortes. Só a física do fenômeno.
- **Ilusões de ótica:** as clássicas são domínio público como ideia, mas a arte precisa ser gerada pelo nosso código.

## Como o ranking é atualizado

- **Todo domingo:** a rotina mede de novo os 10 tópicos e mais 5 candidatos novos (temas que aparecerem nas buscas da semana), reordena o top 10 e refaz a agenda da semana seguinte.
- **Todo dia:** 1 a 3 buscas dentro do tópico de amanhã, para achar os subtemas e formatos que estão subindo agora.
- **Troca no meio da semana:** se um tópico da agenda cair pela metade e uma reserva estiver bem acima, a reserva entra no lugar dele.
- **Dados do próprio canal:** depois de 2 semanas de vídeos, a média de views do Fun Stuff em cada tópico passa a valer metade da nota.
