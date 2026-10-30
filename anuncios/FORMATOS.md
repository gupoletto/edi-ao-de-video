# Formatos de anúncio em vídeo: Meta, TikTok, YouTube/Google, Kwai e outras

> Pesquisado em **30/10/2026** nas páginas oficiais de cada plataforma, por busca restrita aos domínios oficiais. O
> acesso direto às páginas estava bloqueado na rede da sessão. Onde só havia blog de terceiros, isso está marcado.
> As plataformas mudam esses números com frequência: **antes de produzir uma campanha, confira os números no
> gerenciador de anúncios** (pré-visualização de posicionamento) e atualize este arquivo.

## 1. Regra de produção: 3 masters, depois as variações

Toda peça nasce em três masters, renderizados separadamente e nunca esticados:

| Master | Tamanho | Serve para |
|---|---|---|
| **Vertical 9:16** | 1080×1920 (1440×2560 se a peça tiver muito detalhe) | Reels, Stories, TikTok, YouTube Shorts, Kwai, Snapchat, Status |
| **Feed 4:5** | 1080×1350 (Meta recomenda 1440×1800) | Feed do Facebook e do Instagram, Demand Gen |
| **Horizontal 16:9** | 1920×1080 | YouTube in-stream, bumper, in-feed, CTV, LinkedIn, Performance Max |
| *(opcional)* Quadrado 1:1 | 1080×1080 | fallback de Feed, Performance Max, LinkedIn |

A composição é refeita em cada proporção: título, produto e marca reposicionados. Recortar o 16:9 para fazer o
9:16 costuma cortar texto e rosto.

**Exportação padrão:** MP4, H.264 High, 30 fps (ou 60 fps se o original for 60), AAC 48 kHz, áudio em −14 LUFS
(redes) ou −24 LUFS (TV/CTV), cores BT.709, sem barras pretas embutidas.

## 2. Zonas seguras (onde a interface do app cobre o vídeo)

Texto, logo, preço e CTA ficam **dentro** da zona segura. Fora dela, só fundo e textura.

| Plataforma (9:16, 1080×1920) | Topo livre | Base livre | Lateral livre | Fonte |
|---|---|---|---|---|
| Meta **Reels** | 14 % (~270 px) | **35 %** (~670 px) | 6 % de cada lado (~65 px) | facebook.com ads guide, Reels |
| Meta **Stories** (vídeo) | 14 % (250 px) | 20 % (340 px) | — | facebook.com ads guide, Stories |
| Meta Stories (imagem) | 14 % (250 px) | 14 % (250 px) | — | facebook.com, design specs Stories |
| **YouTube Shorts** ads | 10 % | 25 % | **direita 10 %** (botões) | support.google.com 16041697 |
| **TikTok** In-Feed | varia com a proporção e o tamanho da legenda | — | direita (botões) | ads.tiktok.com: arquivos de zona segura para baixar |

**Zona segura universal 9:16** (um só criativo para todos os verticais): **topo 14 %, base 35 %, direita 12 %,
esquerda 6 %**. Na prática, conteúdo importante entre **y = 270 e y = 1250 px** e **x = 65 e x = 950 px**. Ela
cobre Reels, Stories, Shorts e TikTok com legenda média.

O Meta usa zonas seguras diferentes para Stories e Reels, a ponto de ter duas tags 9:16 no catálogo
(developers.facebook.com, Advantage+ catalog).

Feed 4:5 e 1:1: margem de ~100 px nas bordas. 16:9 no YouTube: deixe o canto inferior esquerdo e o superior direito
mais livres (botão "Pular", contador, título do anúncio).

`python3 anuncios/zonas.py` gera um PNG transparente com as zonas de cada plataforma para sobrepor e conferir.

## 3. Meta (Facebook e Instagram)

Fontes: facebook.com/business/ads-guide/update/video, …/instagram-reels, …/instagram-story, help 103816146375741
(proporções por posicionamento), help 682655495435254.

- **Proporção por posicionamento:** Feed **4:5** (1:1 aceito); Stories, Reels e Status **9:16**; in-stream **16:9**.
- **Resolução recomendada no guia atual:** Feed 4:5 1440×1800; Reels e Stories 9:16 1440×2560 (1080×1920 funciona).
- **Arquivo:** MP4, MOV ou GIF, até 4 GB, sem "edit lists" nem caixas especiais no container.
- **Duração:** o Feed aceita de 1 s a 241 min; Reels até 90 s e Stories até 60 s (as páginas do Meta divergem).
  Para desempenho: **15–30 s**, com a mensagem principal nos primeiros 3 s.
- **Texto (guia atual do Feed):** texto principal 50–150 caracteres; título até 27 caracteres. Uma página antiga de
  carrossel ainda fala em 125 e 40.
- **Boas práticas oficiais:**
  - "regra dos 3 segundos": gancho e marca no começo;
  - pensado para som ligado, mas legendado (legendas aumentaram o tempo de visualização em 12 % nos testes do Meta);
  - vertical com som em Reels teve CPA 4,8 % menor e CTR 5,1 % maior (Meta, 2023);
  - posicionamentos Advantage+;
  - teste A/B frequente contra fadiga de criativo.
- **Advantage+ Creative** pode converter para 9:16 e aplicar melhorias automáticas. Desligue o que mexer no texto ou
  na marca quando a peça for precisa.

## 4. TikTok

Fontes: ads.tiktok.com help (TikTok Auction In-Feed Ads, Video Ads Specifications, Spark Ads, TopView, Creative
best practices, Available placements for the CTA button).

- **Proporção:** 9:16 recomendado; 1:1 e 16:9 aceitos.
- **Resolução mínima:** 540×960 (vertical), 640×640 (quadrado), 960×540 (horizontal); a recomendada é 720×1280 ou
  mais, e o padrão prático é 1080×1920.
- **Arquivo:** .mp4, .mov, .mpeg, .avi; até 500 MB; bitrate ≥ 516 kbps.
- **Duração:** a política de formato diz **5–60 s**, mas a ficha técnica do In-Feed (não Spark) aceita até 10 min.
  Recomendado **9–15 s**; um guia antigo para pequenas empresas fala em 21–34 s.
- **Nome exibido:** até 20 caracteres (recomendado 4–10), sem emoji. Precisa bater com a marca da página de destino.
- **Texto do anúncio:** a legenda mostra até 4 linhas antes do "ver mais"; mantenha **< 100 caracteres**. No Spark Ads
  a legenda vem do post orgânico (até 150). No não-Spark não há link clicável nem hashtag.
- **CTA:** 25 opções (padrão "Saiba mais"); a cor é automática.
- **Spark Ads:** impulsiona um post orgânico (o nome e a legenda vêm do post).
- **Boas práticas oficiais:**
  - proposta nos **3 primeiros segundos**, gancho até os 6 s;
  - visual nativo e "feito à mão", parecendo conteúdo de usuário;
  - som ou música sempre (Commercial Music Library: só ela é liberada para anúncio);
  - texto na tela curto (~5–10 palavras por tela);
  - layout respeitando a interface.

## 5. YouTube e Google Ads

Fontes: support.google.com/youtube 2375464 (formatos de anúncio em vídeo), google-ads 11462260 (não puláveis),
16041697 (Shorts ads), 17091672, 17141078 e 13704860 (Demand Gen), 14528532 (Performance Max), 14783551 (ABCD).

| Formato | Duração | Observação |
|---|---|---|
| **In-stream pulável** | pulável após **5 s**; sem máximo (recomendado < 3 min); mínimo de 7 s em uma página | 16:9 1920×1080; 9:16 e 1:1 aceitos |
| **In-stream não pulável** | **≤ 15–30 s** (as páginas divergem; o YouTube Help diz ≤ 60 s; na TV, 15/30/60 s) | |
| **Bumper** | **≤ 6 s**, não pulável | um único recado; marca do início ao fim |
| **In-feed** (Home e Busca) | sem máximo | a miniatura e o título é que geram o clique |
| **Shorts ads** | ≥ 5 s; até 3 min, mas **só os 60 s iniciais tocam**; para ação, **10–30 s** | 9:16 1080×1920; pulável a qualquer momento; o horizontal só aparece sem vertical no grupo |
| **Demand Gen** | ≥ 5 s (< 10 s não roda no in-stream); recomendado **10–60 s** | 16:9, 9:16, 4:5, 1:1; até 3 vídeos por formato; título ≤ 40 (um ≤ 30), título longo ≤ 90, descrição ≤ 90, nome da empresa ≤ 25 |
| **Performance Max** | **≥ 10 s** | 16:9, 9:16 e 1:1; pelo menos um vertical de 10–60 s para Shorts; sem vídeo próprio, o Google gera um de baixa qualidade |

- **Hospedagem:** os vídeos de Demand Gen, Performance Max e YouTube são enviados ao YouTube (pode ser não listado)
  e usados pelo link.
- **ABCD do YouTube** (estudo Google + Ipsos: +30 % em probabilidade de venda no curto prazo):
  - **Atenção:** gancho imediato, ritmo rápido, imagem clara e de alto contraste, áudio e texto;
  - **Branding:** marca cedo e mais de uma vez, falada e mostrada;
  - **Conexão:** pessoas, mensagem simples, humor, surpresa ou curiosidade;
  - **Direção:** CTA específico, falado e escrito.

## 6. Kwai (forte no Brasil)

Fonte oficial: kwai.com/business/pt-BR. Ela só informa o **In-feed Ads: até 60 s, imersivo, som ligado**. O resto
vem de blogs, não oficiais e divergentes: 9:16 1080×1920 (mínimo 720×1280), MP4 ou MOV. **Confirmar no gerenciador
do Kwai for Business antes de produzir.** Linguagem: popular, humor, áudio em português, ritmo de TikTok.

## 7. Outras (sem fonte oficial nesta pesquisa; conferir antes)

- **Snapchat:** 9:16 1080×1920; 3–180 s; até 1 GB; pulável (gancho no 1º segundo).
- **LinkedIn:** os sites divergem (só 1:1 ou de 9:16 a 16:9; 200 ou 500 MB; 3 s a 30 min). Recomendado < 60 s,
  legendado, tom profissional.
- **Pinterest:** vídeo até 2 GB; proporções e duração não confirmadas.

## 8. Matriz rápida: o que entregar por pedido

| Pedido | Entregar |
|---|---|
| "Anúncio Meta" | 9:16 (Reels/Stories) + 4:5 (Feed) + 1:1, 15–30 s, legendado, gancho ≤ 3 s, zona segura do Reels |
| "Anúncio TikTok" ou "Kwai" | 9:16, 9–15 s (até 30), visual nativo, legenda queimada, nome ≤ 20, texto < 100 |
| "Anúncio YouTube" | 16:9 15–30 s (não pulável ou pulável) + bumper 6 s + 9:16 10–30 s para Shorts |
| "Google Ads / PMax / Demand Gen" | 16:9 + 9:16 + 1:1 (+ 4:5), ≥ 10 s, os títulos e descrições nos limites acima |
| "Story" | 9:16, 6–15 s, CTA na faixa 270–1250 px, nada importante abaixo de 1580 px |

## 9. Estrutura de criativo que funciona em todas

1. **0–1 s: gancho visual em movimento.** O quadro 0 já é o gancho (rosto, resultado, pergunta). Nunca logo parado
   nem tela preta.
2. **1–3 s: a promessa** em texto curto e falada.
3. **3–20 s:** prova, demonstração e benefício, com cortes de 1–2 s no vertical. Sem som, a peça precisa se entender
   pelas legendas e pelo texto na tela.
4. **Marca:** cedo (até 5 s) e no fim; no bumper, o tempo todo.
5. **Final: CTA** falado e escrito, com um único verbo ("Baixe", "Compre", "Agende") e a oferta.
6. **Variações para teste:** 3 ganchos × 1 corpo × 2 CTAs. Troque o gancho antes de trocar o resto.

## 10. Regras e conformidade

- **IA:** imagem ou vídeo realista gerado por IA (pessoas, lugares, eventos que parecem reais) precisa do rótulo da
  plataforma (Meta "Feito com IA", TikTok "conteúdo gerado por IA", YouTube "conteúdo alterado ou sintético"). Voz de
  IA e animação claramente gráfica normalmente não exigem. Conferir a política atual de cada uma.
- **Música:** só música licenciada para anúncio (TikTok Commercial Music Library, Meta Sound Collection, YouTube Audio
  Library) ou trilha sintetizada pelo próprio kit (`edicao/ferramentas/sons.py`). Nunca música comercial.
- **Brasil:** publicidade segue o CDC e o CONAR: oferta clara, preço e condições legíveis, "publicidade" identificada
  em parcerias. Setores regulados (saúde, financeiro, apostas, bebidas) têm regras extras. Conferir antes.
- **Texto na imagem:** o Meta não tem mais a regra dos 20 %, mas muito texto ainda reduz a entrega. Prefira pouco
  texto e grande.
