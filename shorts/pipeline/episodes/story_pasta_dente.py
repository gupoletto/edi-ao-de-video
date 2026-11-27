"""How is toothpaste made? (2D, padrão caprichado). Fri 27/11/2026. Search 26/11: "how toothpaste is made" median 133k.

Facts:
- toothpaste tubes are filled from the back: the empty tube stands cap-down, paste is pumped in through the open
  end, which is then flattened, sealed (crimped or heat-sealed) and stamped with a code;
- main ingredients: a mild abrasive (calcium carbonate or hydrated silica), fluoride, humectants that keep it moist
  (glycerin, sorbitol), a foaming detergent (e.g. sodium lauryl sulfate), thickeners and flavor (often mint);
- it is mixed under vacuum so no air bubbles get trapped;
- striped toothpaste: in a common design the stripe paste sits near the nozzle around a small tube; when the white
  paste is squeezed through that tube, the stripe paste is pushed out alongside, so the stripes come out together.
Tone: fun -> alegre.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "divertido"
TUBO = (0.95, 0.95, 0.97)
AZUL = (0.20, 0.55, 0.95)
VERM = (0.95, 0.25, 0.30)
MENTA = (0.55, 0.92, 0.80)
FUNDO = ((0.35, 0.70, 0.95), (0.08, 0.25, 0.50))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def tubo(ctx, x, y, s=1.0, ang=0.0, cheio=1.0, fechado=True):
    """Tubo de pasta em pé com a tampa para baixo; (x, y) = centro."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    anim.bloco_3d(ctx, -40, 230, 80, 50, 14, AZUL)   # tampa
    ctx.new_path()
    ctx.move_to(-110, -260)
    ctx.line_to(110, -260)
    ctx.line_to(60, 230)
    ctx.line_to(-60, 230)
    ctx.close_path()
    ctx.set_source_rgb(*TUBO)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    ctx.set_source_rgba(*AZUL, 0.85)   # faixa da embalagem
    ctx.rectangle(-120, -80, 240, 90)
    ctx.fill()
    if cheio < 1:   # parte vazia (transparente ao encher)
        ctx.set_source_rgba(0.1, 0.1, 0.15, 0.25)
        ctx.rectangle(-120, -260, 240, 490 * (1 - cheio))
        ctx.fill()
    ctx.restore()
    if fechado:
        ctx.set_source_rgb(0.85, 0.85, 0.88)
        ctx.rectangle(-112, -275, 224, 22)
        ctx.fill()
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    m1 = s.mark(1) if len(s.items) > 1 else 99
    vira = ease((t - 0.3) / 0.6)
    tubo(ctx, 540, 990, 1.05, ang=math.pi * (1 - vira), cheio=1.0, fechado=False)
    anim.texto_pop(ctx, t - 0.5, ["FILLED", "FROM", "THE", "BACK"], 540, 470, size=68, largura=1000, cor=WHITE, cor_destaque=MENTA,
                   destaque=3, intervalo=0.16)
    if t > m1:
        anim.seta(ctx, t - m1, 540, 690, ang=math.pi / 2, cor=(1, 0.9, 0.3))


def d_receita(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    itens = [("CHALK", (0.97, 0.97, 0.95)), ("FLUORIDE", (0.70, 0.85, 1.0)), ("GLYCERIN", (0.95, 0.95, 0.80)),
             ("FOAM", (1, 1, 1)), ("MINT", MENTA)]
    for i, (nome, cor) in enumerate(itens):
        ti = t - 0.3 - i * 0.55
        core.evento_som("pop", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.4), 0.001)
        x = 200 + (i % 3) * 340
        y = 760 + (i // 3) * 260
        if i >= 3:
            x += 170
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(k, k)
        anim.esfera(ctx, 0, 0, 70, cor)
        text_center(ctx, nome, 0, 120, 34, WHITE, "ExtraBold")
        ctx.restore()


def d_vacuo(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.20, 0.30, 0.40), (0.05, 0.08, 0.12), bokeh=MENTA)
    anim.sombra_chao(ctx, 540, 1190, 640)
    anim.cilindro(ctx, 540, 660, 500, 480, (0.75, 0.78, 0.84))
    ctx.save()
    ctx.new_path()
    ctx.rectangle(330, 720, 420, 400)
    ctx.clip()
    ctx.set_source_rgb(0.97, 0.98, 0.97)
    ctx.paint()
    sai = ease((t - 1.0) / 2.0)
    for i in range(20):   # bolhas de ar sendo puxadas para fora
        x = 360 + (i * 47) % 360
        y = 1100 - ((i * 53) % 360) - 500 * sai
        ctx.new_path()
        ctx.set_source_rgba(0.6, 0.7, 0.8, 0.8)
        ctx.arc(x, y, 10, 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()
    anim.seta(ctx, t - 0.8, 540, 600, ang=-math.pi / 2, cor=(1, 0.9, 0.3), som="swish")
    anim.texto_pop(ctx, t - 0.3, ["NO", "AIR", "BUBBLES"], 540, 500, size=80, cor=WHITE)


def d_enche(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    ctx.set_source_rgb(0.25, 0.27, 0.30)   # esteira
    ctx.rectangle(0, 1180, W, 24)
    ctx.fill()
    for i in range(4):   # tubos em pé, tampa para baixo, andando
        x = 140 + i * 260 + ((t * 60) % 260)
        cheio = ease((t * 0.8 - i * 0.2) % 1.0) if i == 1 else (1.0 if i > 1 else 0.0)
        tubo(ctx, x, 950, 0.55, cheio=cheio, fechado=i > 1)
    bx = 140 + 260 + ((t * 60) % 260)
    ctx.set_source_rgb(0.55, 0.57, 0.62)   # bico de enchimento
    ctx.rectangle(bx - 20, 640, 40, 120)
    ctx.fill()
    ctx.set_source_rgb(0.97, 0.98, 0.97)
    ctx.rectangle(bx - 8, 760, 16, 40)
    ctx.fill()
    if len(s.items) > 1:
        m = s.mark(1)
        anim.texto_pop(ctx, t - m, ["SEALED", "&", "STAMPED"], 540, 520, size=80, cor=WHITE)
        anim.estouro(ctx, t - m - 0.3, 140 + 2 * 260 + ((t * 60) % 260), 800, cor=(1, 0.9, 0.3), r0=40, r1=110)


def d_listras(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    aperta = 0.5 + 0.5 * math.sin(t * 2.2)
    # corte do bico: tubinho central (branco) com pasta colorida ao redor
    ctx.save()
    ctx.translate(540, 860)
    ctx.new_path()
    ctx.rectangle(-200, -260, 400, 360)
    ctx.set_source_rgb(0.97, 0.98, 0.97)
    ctx.fill()
    for lado, cor in ((-1, VERM), (1, AZUL)):
        ctx.set_source_rgb(*cor)
        ctx.rectangle(lado * 60 - (40 if lado < 0 else 0), 40, 40, 120)
        ctx.fill()
    ctx.set_source_rgb(0.80, 0.82, 0.86)
    ctx.rectangle(-30, -60, 60, 220)
    ctx.fill()
    ctx.restore()
    comp = 80 + 140 * aperta   # pasta listrada saindo
    for j, cor in enumerate((VERM, (0.97, 0.98, 0.97), AZUL)):
        ctx.set_source_rgb(*cor)
        ctx.rectangle(500 + j * 27, 1020, 26, comp)
        ctx.fill()
    for lado in (-1, 1):
        anim.seta(ctx, t - 0.5, 540 + lado * 230, 800, ang=0 if lado < 0 else math.pi, cor=(1, 0.9, 0.3), tam=70,
                  som="swish" if lado < 0 else None)
    anim.texto_pop(ctx, t - 0.3, ["STRIPES", "JOIN", "AT", "THE", "TIP"], 540, 500, size=72, cor=WHITE,
                   cor_destaque=VERM, destaque=0, intervalo=0.15)


SEGMENTS = [
    Seg(["Toothpaste tubes are filled from the wrong end.", "The bottom."], d_gancho,
        {"title": "HOW IS TOOTHPASTE MADE?"}, tail=0.2),
    Seg(["The paste is a mix of fine chalk to scrub, fluoride for your teeth, glycerin to stay moist, a bit of foam, and mint."],
        d_receita, {"big": "THE RECIPE", "color": MENTA}, tail=0.2),
    Seg(["It's mixed inside a vacuum, so not a single air bubble gets trapped."], d_vacuo,
        {"big": "THE MIX", "color": WHITE}, tail=0.2),
    Seg(["Empty tubes stand upside down, cap first. A nozzle fills them through the open bottom.",
         "Then it's squashed flat, sealed, and stamped."], d_enche, {"big": "THE FILL", "color": WHITE}, tail=0.2),
    Seg(["And striped toothpaste? The colors wait near the tip, and get squeezed out together with the white."],
        d_listras, {"big": "THE STRIPES", "color": (1, 0.9, 0.4)}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Do you squeeze from the middle?", "MIDDLE OR BOTTOM?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
