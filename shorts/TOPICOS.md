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
| 6 | **Como funciona em 3D** | 49 mil (busca "how it works 3d"); ~113 mil em "how it works 3d animation" | (01/11) | three.js (`pipeline/tres.py`) |
| 7 | **Terra e natureza em simulação** | a medir no domingo 08/11 | — | Vulcões, placas, ondas, clima |

## Agenda da semana (a partir de 02/11)

**Teste de 2 vídeos por dia de 02/11 a 08/11** (aprovado em 31/10; horários no `upload.py`). Em cada dia:
1. um **"what if / why" com o mascote Quark** (`pipeline/personagem.py`), roteiro com arco de conflito;
2. **ranking** ou **interativo**, alternando dia sim, dia não. Começa pelo ranking na segunda; na quinta o 3D toma o
   lugar desse segundo vídeo.

| Dia | Tópico | 2º vídeo |
|---|---|---|
| Segunda 02/11 | Espaço | Ranking |
| Terça 03/11 | Ilusões de ótica | Interativo |
| Quarta 04/11 | Simulações de física | Ranking |
| Quinta 05/11 | Como funciona (3D) | 3D "como funciona" |
| Sexta 06/11 | Terra e natureza em simulação | Interativo |
| Sábado 07/11 | Comparação de tamanho e escala | Ranking |
| Domingo 08/11 | Satisfying | Interativo |

No domingo 08/11 a rotina compara a semana de 2/dia com a semana anterior (3/dia), olhando a média de views por vídeo,
a taxa de engajamento e, se a API de Analytics estiver liberada, a taxa de visualização e a duração média. Ela registra
o resultado em `tendencias/` e no relatório, e recomenda ao usuário: manter 2, voltar para 3 ou testar 1. **Quem decide
é o usuário.** Até ele decidir, o `upload.py` volta sozinho para 3 slots a partir de 09/11.

## Os vídeos do dia: sempre diferentes entre si

Os vídeos do dia são do mesmo tópico, mas cada um tem **subtema e formato diferentes**:

1. **Ranking** (#5 → #1).
2. **"What if / Why"**. Desde 02/11 é contado pelo mascote Quark, com arco de conflito (gancho → subida → conflito →
   virada → recompensa).
3. **Interativo**: quiz, "can you spot it?", "guess which…".
4. **Como funciona em 3D**, no lugar de um dos outros.

Nenhum subtema se repete em 30 dias (controle em `historico.md`). O padrão de título também não se repete em dias
seguidos.

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
