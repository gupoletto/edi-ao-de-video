# Cartoon 3D (personagens 2D em mundo 3D)

Projeto Remotion + three.js para Shorts no estilo "personagens 2D chapados num mundo 3D com contorno de tinta".
Base: código do vídeo da ponte da skill gratuita [mromidev/claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts)
(licença MIT, cópia em `LICENSE-claude-animated-shorts`), em `src/videos/bridge/`.
Os quadros de referência do canal estudado pela skill NÃO estão aqui (são de terceiros).

- `npm install` (node_modules fica fora do git)
- Quadros de teste sem GPU: `CHROME=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell node scripts/stills.mjs BridgeShort <prefixo> 100,700 0.5`

Situação (23/11/2026): render validado sem GPU (Chromium headless shell + `gl: "swangle"`): ~3,5 s por quadro em 1080x1920, ~1h45 para 60 s. Vídeo: `node scripts/render.mjs <Comp> <saida.mp4> [inicio-fim] [escala, ex. 2/3]` (CONC=1 é o mais rápido; TMPDIR numa pasta limpável).
