// Render de vídeo sem GPU: node scripts/render.mjs <Comp> <saida.mp4> [inicio-fim] [escala]
import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia } from "@remotion/renderer";
import path from "node:path";

const [comp, saida, faixa, escala = "1"] = process.argv.slice(2);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const chrome = { browserExecutable: process.env.CHROME || "/opt/pw-browsers/chromium", chromiumOptions: { gl: process.env.GL || "swangle" } };
const c = (await getCompositions(serveUrl, chrome)).find((x) => x.id === comp);
const frameRange = faixa ? faixa.split("-").map(Number) : null;
const t0 = Date.now();
let ultimo = 0;
await renderMedia({
  composition: c, serveUrl, codec: "h264", crf: 18, outputLocation: saida, scale: escala.includes("/") ? Number(escala.split("/")[0]) / Number(escala.split("/")[1]) : Number(escala), frameRange,
  concurrency: Number(process.env.CONC || 2), timeoutInMilliseconds: 900000, ...chrome,
  onProgress: ({ renderedFrames }) => {
    if (renderedFrames - ultimo >= 10) { ultimo = renderedFrames; console.log(`${renderedFrames} quadros, ${((Date.now() - t0) / 1000).toFixed(0)} s`); }
  },
});
console.log(`fim: ${((Date.now() - t0) / 1000).toFixed(1)} s`);
