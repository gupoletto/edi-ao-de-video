---
name: anuncios
description: Cria anúncios em vídeo animados (motion graphics) para Meta Ads (Reels, Stories, Feed), TikTok, Kwai, YouTube (in-stream, bumper, Shorts) e Google Ads (Demand Gen, Performance Max). Use quando o usuário pedir um anúncio, criativo, peça de campanha, story patrocinado ou "vídeo para ads", em qualquer formato (vertical, quadrado, horizontal).
---

# Anúncios em vídeo

Leia primeiro `anuncios/FORMATOS.md`: proporções, durações, zonas seguras, limites de texto e boas práticas de cada
plataforma. Leia também as seções 3h (ofício de movimento) e 3i (referência Motion) de `edicao/ESTILO.md`.

## Passos

1. **Brief em 5 linhas:** produto/oferta, público, plataforma(s) e objetivo (alcance, clique, conversão), CTA,
   marca (logo, cores em hex, fonte). Pergunte só o que faltar e não der para inferir. As plataformas definem os
   masters (`FORMATOS.md`, seção 8).
2. **Especificação antes de animar** (estilo "Motion"):
   - Estilo: fundo e acento em hex, tipografia, tipo de movimento ("ease-out longo, sem bounce exagerado").
   - Linha do tempo em segundos, com gancho 0–1 s, promessa até 3 s, prova, marca e CTA (`FORMATOS.md`, seção 9).
   - Texto de cada tela, com no máximo ~5 palavras por linha no vertical.
   Mostre a especificação ao usuário e espere o ok.
3. **Animação em código**, deterministica por tempo:
   - cairo como em `shorts/pipeline/core.py` e `edicao/ferramentas/elementos.py`;
   - three.js para 3D (`shorts/pipeline/tres.py`);
   - trilha e efeitos em `edicao/ferramentas/sons.py`.
   Nada de mídia de terceiros sem licença. Cada master tem a sua composição: não estique um no outro.
4. **Conferir:**
   - `python3 anuncios/zonas.py --conferir <peça> --em <s> --zona <plataforma>` nos quadros com texto, logo e CTA;
   - legível sem som;
   - marca até 5 s;
   - duração dentro do limite;
   - −14 LUFS.
5. **Exportar** (MP4 H.264, AAC 48 kHz, BT.709) com o nome `<marca>_<plataforma>_<proporção>_<duração>s_v<n>.mp4`.
   Para Google, o vídeo sobe para o YouTube como não listado. Entregue também os textos (título, texto principal,
   descrição) nos limites de cada plataforma, e de 2 a 3 variações de gancho para teste.

Realismo gerado por IA (pessoas e lugares que parecem reais) exige o rótulo de IA da plataforma: avise o usuário.
