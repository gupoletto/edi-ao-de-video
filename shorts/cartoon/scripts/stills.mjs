// Quadros de teste sem GPU: node scripts/stills.mjs <Comp> <saida_prefixo> <f1,f2,...> [escala]
import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import path from "node:path";

const [comp, prefixo, frames, escala = "0.5"] = process.argv.slice(2);
const t0 = Date.now();
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const chrome = { browserExecutable: process.env.CHROME || "/opt/pw-browsers/chromium", chromiumOptions: { gl: "swiftshader" } };
const comps = await getCompositions(serveUrl, chrome);
const c = comps.find((x) => x.id === comp);
console.log(`bundle ${((Date.now() - t0) / 1000).toFixed(1)} s`);
for (const f of frames.split(",").map(Number)) {
  const t = Date.now();
  await renderStill({ composition: c, serveUrl, output: `${prefixo}${f}.png`, frame: f, scale: Number(escala), ...chrome, timeoutInMilliseconds: 600000 });
  console.log(`frame ${f}: ${((Date.now() - t) / 1000).toFixed(1)} s`);
}
