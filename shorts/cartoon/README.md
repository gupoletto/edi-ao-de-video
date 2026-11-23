# Cartoon 3D (personagens 2D em mundo 3D)

Projeto Remotion + three.js para Shorts no estilo "personagens 2D chapados num mundo 3D com contorno de tinta".
Base: código do vídeo da ponte da skill gratuita [mromidev/claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts)
(licença MIT, cópia em `LICENSE-claude-animated-shorts`), em `src/videos/bridge/`.
Os quadros de referência do canal estudado pela skill NÃO estão aqui (são de terceiros).

- `npm install` (node_modules fica fora do git)
- Quadros de teste sem GPU: `CHROME=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell node scripts/stills.mjs BridgeShort <prefixo> 100,700 0.5`

Situação (23/11/2026): projeto monta; o render de teste ainda não foi validado neste ambiente (sem GPU).
