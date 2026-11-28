"""How is pizza made? (2D, padrão caprichado). Sat 28/11/2026. Search 28/11: "how pizza is made" median 2.14M.

Facts (Neapolitan pizza, AVPN rules):
- a Neapolitan pizza bakes in about 60-90 seconds in a wood-fired oven at around 430-485 C;
- dough: flour, water, salt, yeast, left to rise for many hours (often 8-24+);
- stretched by hand, never with a rolling pin, to keep the air in the rim (the "cornicione");
- toppings for a margherita: tomato, mozzarella, basil, olive oil;
- legend says pizzaiolo Raffaele Esposito made it in 1889 for Queen Margherita, in the colors of the Italian flag
  (historians doubt the details; said as legend);
- the art of the Neapolitan pizzaiuolo is on UNESCO's intangible heritage list (2017);
- the dark "leopard" spots on the crust are bubbles that char in the heat.
Tone: animado -> pop.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "animado"
MASSA = (0.96, 0.86, 0.62)
TOMATE = (0.86, 0.16, 0.10)
MUSSA = (0.99, 0.97, 0.90)
MANJ = (0.20, 0.62, 0.28)
FOGO = (1.0, 0.55, 0.15)
FUNDO = ((0.30, 0.12, 0.08), (0.08, 0.03, 0.02))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def pizza(ctx, x, y, r, molho=1.0, queijo=1.0, manj=1.0, assada=0.0, t=0.0):
    """Pizza vista de cima (elipse leve, perspectiva)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, 0.62)
    anim.sombra_chao(ctx, 0, r * 0.9, r * 2.4)
    borda = tuple(a + (b - a) * assada for a, b in zip(MASSA, (0.85, 0.55, 0.25)))
    anim.esfera(ctx, 0, 0, r, borda)
    if molho > 0:
        ctx.new_path()
        ctx.arc(0, 0, r * 0.82 * molho, 0, 2 * math.pi)
        ctx.set_source_rgb(*TOMATE)
        ctx.fill()
    for i in range(int(9 * queijo)):
        a = i * 2.4
        rr = r * 0.5 * ((i * 37 % 10) / 10)
        ctx.new_path()
        ctx.arc(rr * math.cos(a), rr * math.sin(a), r * 0.17, 0, 2 * math.pi)
        ctx.set_source_rgb(*MUSSA)
        ctx.fill()
    for i in range(int(5 * manj)):
        a = i * 1.3 + 0.5
        ctx.save()
        ctx.translate(r * 0.45 * math.cos(a), r * 0.45 * math.sin(a))
        ctx.rotate(a)
        ctx.scale(1, 0.55)
        ctx.new_path()
        ctx.arc(0, 0, r * 0.1, 0, 2 * math.pi)
        ctx.set_source_rgb(*MANJ)
        ctx.fill()
        ctx.restore()
    if assada > 0.5:   # manchas de "leopardo" na borda
        for i in range(18):
            a = i * 0.35
            ctx.new_path()
            ctx.arc(r * 0.92 * math.cos(a), r * 0.92 * math.sin(a), 8 + i % 4, 0, 2 * math.pi)
            ctx.set_source_rgba(0.15, 0.08, 0.04, (assada - 0.5) * 1.6)
            ctx.fill()
    ctx.restore()


def forno(ctx, t, x=540, y=900, brilho=1.0):
    anim.sombra_chao(ctx, x, y + 260, 760)
    ctx.new_path()   # cúpula de tijolos
    ctx.arc(x, y + 200, 340, math.pi, 2 * math.pi)
    ctx.line_to(x + 340, y + 260)
    ctx.line_to(x - 340, y + 260)
    ctx.close_path()
    ctx.set_source_rgb(0.62, 0.30, 0.20)
    ctx.fill()
    ctx.set_source_rgba(0.40, 0.18, 0.12, 0.7)
    ctx.set_line_width(4)
    for r in range(120, 340, 55):
        ctx.arc(x, y + 200, r, math.pi, 2 * math.pi)
        ctx.stroke()
    ctx.new_path()   # boca do forno com fogo
    ctx.arc(x, y + 220, 170, math.pi, 2 * math.pi)
    ctx.close_path()
    ctx.set_source_rgb(0.10, 0.04, 0.02)
    ctx.fill()
    anim.brilho(ctx, x, y + 170, 260, FOGO, 0.8 * brilho)
    anim.faiscas(ctx, t, x - 60, y + 200, n=20, vel=260, cor=(1, 0.8, 0.4), vida=1.0)


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=FOGO)
    forno(ctx, t)
    m1 = s.mark(1) if len(s.items) > 1 else 99
    anim.contador(ctx, t - 0.1, 540, 540, 90, dur=1.0, fmt="{:.0f}", sufixo=" SECONDS", size=100, cor=WHITE)
    if t > m1:
        anim.contador(ctx, t - m1, 540, 680, 485, dur=0.9, sufixo=" °C", size=90, cor=FOGO)


def d_massa(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=FOGO)
    k = ease(t / 4.0)
    anim.sombra_chao(ctx, 540, 1100, 500)
    ctx.save()
    ctx.translate(540, 980)
    ctx.scale(1 + 0.4 * k, 0.75 + 0.25 * k)
    anim.esfera(ctx, 0, 0, 150, MASSA)
    ctx.restore()
    anim.contador(ctx, t - 0.4, 540, 560, 24, dur=1.2, fmt="{:.0f}", sufixo=" HOURS", size=100, cor=WHITE)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["NO", "ROLLING", "PIN"], 540, 690, size=74, cor=MASSA)


def d_abrir(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=FOGO)
    k = ease(t / 2.5)
    pizza(ctx, 540, 950, 150 + 150 * k, molho=0, queijo=0, manj=0, t=t)
    for lado in (-1, 1):   # mãos (círculos) empurrando a borda
        a = t * 3 + (0 if lado > 0 else math.pi)
        anim.esfera(ctx, 540 + (150 + 150 * k) * 0.6 * math.cos(a), 950 + 60 * math.sin(a), 46, (0.95, 0.78, 0.62))
    anim.anel_destaque(ctx, t - 2.0, 540, 950, 250, cor=(1, 0.9, 0.4))
    anim.texto_pop(ctx, t - 0.4, ["AIR", "IN", "THE", "RIM"], 540, 560, size=84, cor=WHITE, intervalo=0.16)


def d_cobertura(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=FOGO)
    pizza(ctx, 540, 950, 300, molho=ease((t - 0.3) / 0.7), queijo=ease((t - 1.3) / 0.8), manj=ease((t - 2.3) / 0.7),
          t=t)
    for i, (cor, t0) in enumerate(((TOMATE, 0.3), (MUSSA, 1.3), (MANJ, 2.3))):
        core.evento_som("pop", t - t0)
    anim.texto_pop(ctx, t - 0.3, ["RED", "WHITE", "GREEN"], 540, 560, size=84, cor=WHITE, intervalo=1.0)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["1889?"], 540, 690, size=80, cor=(1, 0.9, 0.4))


def d_assar(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.35, 0.10, 0.04), (0.10, 0.03, 0.01), bokeh=FOGO)
    anim.tremor(ctx, t - 0.2, forca=6, dur=0.3, som="swish")
    anim.brilho(ctx, 540, 950, 520, FOGO, 0.55)
    pizza(ctx, 540, 950, 300, assada=ease(t / 3.0), t=t)
    for i in range(10):   # bolhas na borda estufando
        a = i * 0.63 + t
        ctx.new_path()
        ctx.set_source_rgba(1, 0.9, 0.7, 0.5)
        ctx.arc(540 + 285 * math.cos(a), 950 + 285 * 0.62 * math.sin(a), 10 + 6 * math.sin(t * 4 + i), 0, 2 * math.pi)
        ctx.fill()
    anim.contador(ctx, t - 0.2, 540, 560, 90, dur=2.5, fmt="{:.0f}", sufixo=" S", size=100, cor=WHITE, som=None)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["LEOPARD", "SPOTS"], 540, 690, size=74, cor=(1, 0.85, 0.5))


def d_fim(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=FOGO)
    pizza(ctx, 540, 950, 300, assada=1.0, t=t)
    anim.fumaca(ctx, t, 540, 880, cor=(1, 1, 1), alpha=0.18)
    anim.texto_pop(ctx, t - 0.3, ["UNESCO", "HERITAGE"], 540, 560, size=88, cor=WHITE, cor_destaque=(1, 0.9, 0.4),
                   destaque=0)


SEGMENTS = [
    Seg(["A real Neapolitan pizza bakes in about ninety seconds.", "In an oven over four hundred fifty degrees."],
        d_gancho, {"title": "HOW IS PIZZA MADE?"}, tail=0.2),
    Seg(["It starts the day before: flour, water, salt and yeast, left to rise for up to a day.",
         "And it's never rolled with a pin."], d_massa, {"big": "THE DOUGH", "color": MASSA}, tail=0.2),
    Seg(["It's stretched by hand, pushing the air to the edge. That's what makes the puffy crust."], d_abrir,
        {"big": "THE STRETCH", "color": MASSA}, tail=0.2),
    Seg(["Then tomato, mozzarella and basil. Red, white and green, like the Italian flag.",
         "Legend says it was made for a queen."], d_cobertura, {"big": "MARGHERITA", "color": TOMATE}, tail=0.2),
    Seg(["In the wood oven, the edge puffs up in seconds,", "and the bubbles char into little leopard spots."],
        d_assar, {"big": "THE OVEN", "color": FOGO}, tail=0.2),
    Seg(["Making it is so special, it's on the UNESCO list of world heritage."], d_fim,
        {"big": "LEGENDARY", "color": (1, 0.9, 0.4)}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Pineapple on pizza: yes or no?", "PINEAPPLE: YES OR NO?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO, bokeh=FOGO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
