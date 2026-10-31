"""3D por código (formato "how it works 3D"): cena em three.js, renderizada quadro a quadro no Chromium headless.

O Python calcula o estado de cada quadro (física de verdade: ângulos, posições) e manda para a cena, que só posa
os objetos e desenha. Os quadros viram JPEGs numa pasta temporária e o core.py os desenha em tela cheia, com o
cabeçalho, as legendas e os rótulos por cima.

- three.js (MIT) vem do npm para ~/.cache/three, na primeira vez;
- a cena é um arquivo .js em shorts/pipeline/cenas3d/ que define window.montar(THREE, cena, camera) e
  window.posar(estado); peças de cenário prontas (céu, nuvens, grama, estrada, árvores, morros) ficam em
  cenas3d/ambiente.js (`import * as A from 'http://cena.local/ambiente.js'`);
- render: Node + Playwright (já instalados) com WebGL por SwiftShader.
"""
import json
import os
import subprocess
import tempfile

import cairo

from core import CACHE, FPS, H, W

AQUI = os.path.dirname(os.path.abspath(__file__))
THREE = os.path.join(CACHE, "three", "package", "build", "three.module.js")

RENDER_JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch({args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader']});
  const page = await browser.newPage({viewport: {width: cfg.w, height: cfg.h}});
  await page.route('http://cena.local/**', r => {
    const nome = r.request().url().split('/').pop();
    const corpo = nome === 'index.html' ? cfg.html : fs.readFileSync(cfg.arquivos[nome], 'utf8');
    r.fulfill({body: corpo, contentType: nome.endsWith('.html') ? 'text/html' : 'application/javascript'});
  });
  await page.goto('http://cena.local/index.html');
  await page.waitForFunction('window.pronto === true', null, {timeout: 60000});
  for (let i = 0; i < cfg.estados.length; i++) {
    await page.evaluate(e => window.quadro(e), cfg.estados[i]);
    await page.screenshot({path: `${cfg.saida}/${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92});
    if (i % 150 === 0) console.log(`  3D ${i}/${cfg.estados.length}`);
  }
  await browser.close();
})();
"""

HTML = """<!doctype html><html><head><style>html,body{margin:0;background:#0b0f1c;overflow:hidden}</style>
<script type="importmap">{"imports":{"three":"http://cena.local/three.module.js"}}</script></head><body>
<script type="module">
import * as THREE from 'three';
import 'http://cena.local/cena.js';
const r = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
r.setSize(%d, %d); r.setPixelRatio(1);
r.toneMapping = THREE.ACESFilmicToneMapping; r.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(r.domElement);
const cena = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, %d / %d, 0.1, 200);
window.montar(THREE, cena, camera, r);
window.quadro = (e) => { window.posar(e); r.render(cena, camera); };
window.pronto = true;
</script></body></html>"""


def preparar():
    if not os.path.exists(THREE):
        pasta = os.path.join(CACHE, "three")
        os.makedirs(pasta, exist_ok=True)
        subprocess.run(["npm", "pack", "three@0.170.0", "--silent"], cwd=pasta, check=True)
        subprocess.run(["tar", "xzf", "three-0.170.0.tgz"], cwd=pasta, check=True)


class Filme:
    """Quadros 3D de um vídeo inteiro: estados(t_global) -> dict por quadro; depois quadro(ctx, t_global)."""

    def __init__(self, cena, estado):
        self.cena = os.path.join(AQUI, "cenas3d", cena)
        self.estado = estado
        self.pasta = None
        self._cache = (None, None, None)

    def renderizar(self, segs, total, tempos=None):
        """Renderiza todos os quadros (ou só os instantes em `tempos`, para conferir o enquadramento)."""
        reusar = os.environ.get("TRES_PASTA")  # refazer só a parte 2D (legenda, títulos) com quadros 3D já prontos
        if reusar and tempos is None and os.path.exists(os.path.join(reusar, "00000.jpg")):
            self.pasta = reusar
            return
        preparar()
        self.pasta = tempfile.mkdtemp(prefix="tres_")
        ts = tempos if tempos is not None else [i / FPS for i in range(int(total * FPS) + 2)]
        cfg = {"w": W, "h": H, "saida": self.pasta, "html": HTML % (W, H, W, H),
               "arquivos": {"three.module.js": THREE, "cena.js": self.cena,
                            "ambiente.js": os.path.join(AQUI, "cenas3d", "ambiente.js")},
               "estados": [self.estado(t, segs) for t in ts]}
        cfg_p = os.path.join(self.pasta, "cfg.json")
        js_p = os.path.join(self.pasta, "render.js")
        with open(cfg_p, "w") as f:
            json.dump(cfg, f)
        with open(js_p, "w") as f:
            f.write(RENDER_JS)
        raiz = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        subprocess.run(["node", js_p, cfg_p], check=True, env=dict(os.environ, NODE_PATH=raiz))

    def quadro(self, ctx, t):
        i = max(0, int(round(t * FPS)))
        if self._cache[0] != i:
            jpg = os.path.join(self.pasta, f"{i:05d}.jpg")
            if not os.path.exists(jpg):
                return
            from PIL import Image
            import numpy as np
            rgb = np.asarray(Image.open(jpg).convert("RGB"))
            bgra = np.dstack([rgb[..., 2], rgb[..., 1], rgb[..., 0], np.full(rgb.shape[:2], 255, np.uint8)])
            bgra = np.ascontiguousarray(bgra)
            self._cache = (i, cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_RGB24, W, H, W * 4),
                           bgra)
        ctx.set_source_surface(self._cache[1], 0, 0)
        ctx.paint()
