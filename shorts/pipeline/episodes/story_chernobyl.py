"""Chernobyl blew up during a safety test (2D animated story). Sat 21/11/2026, storytelling (history, disaster).
Search 21/11: "chernobyl explained" median 3.9k (top "Chernobyl Blew Up Testing Its Own Backup Plan" 142k).
Monetization: no injuries or bodies on screen, no gore; the story is about the machine and the decisions.

Facts (INSAG-7 report, World Nuclear Association):
- 26 April 1986, 1:23 am, reactor No. 4 of the Chernobyl plant (RBMK design), Soviet Ukraine;
- the test: if the grid power failed, the backup diesel generators needed about a minute to start; could the turbine,
  still spinning down, power the cooling pumps during that gap?
- the test was delayed; the reactor's power fell much lower than planned, and to bring it back up the operators
  pulled out almost all of the control rods (the "brakes"), far beyond the safe limit;
- RBMK flaw: when the cooling water boils into steam, the reactor gets more powerful (positive void coefficient),
  which makes more steam: a loop;
- when the operators pressed the emergency shutdown button (AZ-5), the rods' graphite tips entered first and pushed
  water out of the bottom of the core, briefly raising the power instead of cutting it;
- the power surged many times over in seconds; steam explosions blew off the roughly 1,000-ton reactor lid and the
  graphite caught fire;
- the town of Pripyat (about 49,000 people) was evacuated the next afternoon, about 36 hours later; a 30 km exclusion
  zone still exists.
Tone: disaster -> suspense music.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

core.MUSICA = "desastre"   # tom -> suspense
AZUL = (0.35, 0.75, 1.0)
LARANJA = (1.0, 0.55, 0.15)
CHAO = 1150


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def noite(ctx, vermelho=0.0):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.02 + 0.25 * vermelho, 0.03, 0.08)
    g.add_color_stop_rgb(1, 0.06 + 0.3 * vermelho, 0.07, 0.14)
    ctx.set_source(g)
    ctx.paint()
    ctx.set_source_rgba(1, 1, 1, 0.6)
    for i in range(80):
        ctx.arc((i * 397) % W, (i * 211) % 800, 1.3, 0, 2 * math.pi)
        ctx.fill()


def usina(ctx, t, tampa=0.0, brilho=0.0):
    ctx.set_source_rgb(0.05, 0.05, 0.07)
    ctx.rectangle(0, CHAO, W, H - CHAO)
    ctx.fill()
    ctx.set_source_rgb(0.22, 0.23, 0.27)   # prédios
    ctx.rectangle(140, 900, 300, 250)
    ctx.rectangle(440, 840, 380, 310)
    ctx.fill()
    ctx.set_source_rgb(0.30, 0.31, 0.35)   # chaminé listrada
    ctx.rectangle(560, 560, 50, 280)
    ctx.fill()
    for i in range(4):
        ctx.set_source_rgb(0.7, 0.15, 0.12)
        ctx.rectangle(560, 580 + i * 70, 50, 20)
        ctx.fill()
    ctx.set_source_rgba(1, 0.9, 0.6, 0.8)   # janelas
    for i in range(10):
        ctx.rectangle(170 + (i % 5) * 52, 950 + (i // 5) * 60, 18, 12)
    ctx.fill()
    if brilho > 0:
        import cairo
        g = cairo.RadialGradient(700, 840, 10, 700, 840, 420)
        g.add_color_stop_rgba(0, 1, 0.8, 0.5, brilho)
        g.add_color_stop_rgba(1, 1, 0.3, 0.1, 0)
        ctx.set_source(g)
        ctx.paint()
    ctx.save()   # tampa do reator
    ctx.translate(700, 840 - 260 * tampa)
    ctx.rotate(2.5 * tampa)
    ctx.set_source_rgb(0.4, 0.4, 0.44)
    ctx.rectangle(-90, -14, 180, 28)
    ctx.fill()
    ctx.restore()


def relogio(ctx, txt, y=520):
    round_rect(ctx, 330, y - 56, 420, 120, 24)
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.85)
    ctx.fill()
    text_center(ctx, txt, W / 2, y + 20, 72, (1.0, 0.3, 0.25), "ExtraBold")


def caixa(ctx, l1, l2, cor, y=540):
    round_rect(ctx, 150, y - 56, 780, 136, 26)
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.82)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")


def nucleo(ctx, t, barras, bolhas=0.0, calor=0.0, ponta=None):
    """Corte do reator: núcleo com água, barras de controle (0 = fora, 1 = dentro) e bolhas de vapor."""
    x0, y0, w, h = 290, 700, 500, 450
    ctx.set_source_rgb(0.15, 0.16, 0.20)
    round_rect(ctx, x0 - 20, y0 - 20, w + 40, h + 40, 20)
    ctx.fill()
    ctx.set_source_rgb(*[a + (b - a) * calor for a, b in zip((0.10, 0.30, 0.55), (0.85, 0.35, 0.10))])
    ctx.rectangle(x0, y0, w, h)
    ctx.fill()
    for i in range(int(60 * bolhas)):
        x = x0 + 20 + (i * 83) % (w - 40)
        y = y0 + h - ((t * 160 + i * 47) % h)
        ctx.set_source_rgba(1, 1, 1, 0.55)
        ctx.arc(x, y, 6 + i % 5, 0, 2 * math.pi)
        ctx.fill()
    ctx.save()
    ctx.rectangle(0, 640, W, H - 640)   # barras só aparecem abaixo da caixa de texto
    ctx.clip()
    for i in range(6):   # barras
        bx = x0 + 50 + i * 80
        fundo_barra = y0 - 260 + (h + 220) * barras
        ctx.set_source_rgb(0.75, 0.75, 0.80)
        ctx.rectangle(bx - 12, fundo_barra - 420, 24, 420)
        ctx.fill()
        if ponta is not None:
            ctx.set_source_rgb(0.15, 0.15, 0.15)   # ponta de grafite
            ctx.rectangle(bx - 12, fundo_barra - 60, 24, 60)
            ctx.fill()
    ctx.restore()


def medidor(ctx, valor, t, rotulo="POWER"):
    """Barra vertical de potência à direita; valor 0..1 (1 = fora da escala)."""
    x, y0, h = 900, 1110, 420
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.8)
    round_rect(ctx, x - 30, y0 - h - 20, 60, h + 40, 16)
    ctx.fill()
    v = min(1.0, valor)
    cor = (0.3, 0.9, 0.4) if v < 0.5 else (1.0, 0.75, 0.2) if v < 0.8 else (1.0, 0.25, 0.2)
    ctx.set_source_rgb(*cor)
    ctx.rectangle(x - 18, y0 - h * v, 36, h * v)
    ctx.fill()
    text_center(ctx, rotulo, x, y0 + 45, 24, WHITE, "Bold")


def d_gancho(ctx, t, s):
    noite(ctx)
    usina(ctx, t)
    relogio(ctx, "1:23 AM")


def d_teste(ctx, t, s):
    noite(ctx)
    # tomada caiu -> bombas param -> geradores levam 60 s; a turbina girando cobriria o buraco?
    k = ease(t / 1.0)
    cx = 300
    ctx.set_source_rgb(0.6, 0.62, 0.68)   # turbina girando
    for j in range(8):
        a = t * (6 - 3 * ease(t / 6)) + j * math.pi / 4
        ctx.save()
        ctx.translate(cx, 900)
        ctx.rotate(a)
        ctx.rectangle(0, -10, 110, 20)
        ctx.restore()
    ctx.fill()
    text_center(ctx, "TURBINE", cx, 1080, 30, WHITE, "ExtraBold", alpha=k)
    ctx.set_source_rgba(*AZUL, k)   # fio até a bomba
    ctx.set_line_width(8)
    ctx.set_dash([24, 16], -t * 80)
    ctx.move_to(420, 900)
    ctx.line_to(640, 900)
    ctx.stroke()
    ctx.set_dash([])
    ctx.arc(760, 900, 90, 0, 2 * math.pi)   # bomba
    ctx.fill()
    text_center(ctx, "PUMPS", 760, 1080, 30, WHITE, "ExtraBold", alpha=k)
    n = max(0, 60 - int(t * 10))
    caixa(ctx, f"BACKUP IN {n} S", "COULD THE SPINNING TURBINE COVER THE GAP?", YELLOW)


def d_barras(ctx, t, s):
    noite(ctx)
    k = ease((t - 1.5) / 2.5)
    nucleo(ctx, t, 1 - 0.85 * k)
    medidor(ctx, 0.08 + 0.25 * k, t)
    caixa(ctx, "THE BRAKES CAME OUT", "ALMOST EVERY CONTROL ROD", PINK)


def d_vapor(ctx, t, s):
    noite(ctx)
    b = 0.2 + 0.8 * ease(t / 4.0)
    nucleo(ctx, t, 0.15, bolhas=b, calor=0.3 * b)
    medidor(ctx, 0.3 + 0.35 * b, t)
    caixa(ctx, "MORE STEAM = MORE POWER", "A DESIGN FLAW THAT FEEDS ITSELF", LARANJA)


def d_botao(ctx, t, s):
    noite(ctx, vermelho=ease((t - 2.0) / 1.5) * 0.6)
    desce = ease((t - 1.0) / 2.5) * 0.35
    pico = ease((t - 1.6) / 1.5)
    nucleo(ctx, t, 0.15 + desce, bolhas=1.0, calor=0.3 + 0.7 * pico, ponta=True)
    medidor(ctx, 0.65 + 0.6 * pico, t)
    if t < 1.2:   # o botão AZ-5
        r = 70 * (1 - 0.15 * ease(t / 0.3))
        ctx.set_source_rgb(0.85, 0.12, 0.10)
        ctx.arc(W / 2, 840, r, 0, 2 * math.pi)
        ctx.fill()
        text_center(ctx, "AZ-5", W / 2, 855, 40, WHITE, "ExtraBold")
    caixa(ctx, "THE OFF BUTTON", "MADE IT WORSE, FOR A FEW SECONDS", (1.0, 0.3, 0.25))


def d_explode(ctx, t, s):
    k = ease(t / 1.5)
    noite(ctx, vermelho=0.8)
    usina(ctx, t, tampa=k, brilho=0.9 * (1 - ease((t - 1.5) / 3)) + 0.3)
    flash = max(0.0, 1 - t / 0.5)
    if flash > 0:
        ctx.set_source_rgba(1, 1, 1, flash)
        ctx.paint()
    caixa(ctx, "1,000-TON LID", "THROWN INTO THE AIR", (1.0, 0.3, 0.25))


def d_cidade(ctx, t, s):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.50, 0.55, 0.60)
    g.add_color_stop_rgb(1, 0.25, 0.27, 0.30)
    ctx.set_source(g)
    ctx.paint()
    ctx.set_source_rgb(0.32, 0.34, 0.36)   # prédios vazios
    for i in range(5):
        ctx.rectangle(80 + i * 190, 820 - (i % 2) * 80, 140, 400)
    ctx.fill()
    ctx.set_source_rgb(0.15, 0.16, 0.18)
    for i in range(5):
        for r in range(6):
            ctx.rectangle(100 + i * 190, 860 - (i % 2) * 80 + r * 55, 30, 30)
            ctx.rectangle(150 + i * 190, 860 - (i % 2) * 80 + r * 55, 30, 30)
    ctx.fill()
    cx, cy, R = 760, 760, 150   # roda-gigante parada
    ctx.set_source_rgb(0.85, 0.75, 0.25)
    ctx.set_line_width(6)
    ctx.arc(cx, cy, R, 0, 2 * math.pi)
    ctx.stroke()
    for j in range(10):
        a = j * math.pi / 5 + 0.002 * t
        ctx.move_to(cx, cy)
        ctx.line_to(cx + R * math.cos(a), cy + R * math.sin(a))
        ctx.stroke()
        ctx.rectangle(cx + R * math.cos(a) - 14, cy + R * math.sin(a), 28, 24)
        ctx.fill()
    ctx.move_to(cx - 90, CHAO)
    ctx.line_to(cx, cy)
    ctx.line_to(cx + 90, CHAO)
    ctx.stroke()
    caixa(ctx, "49,000 PEOPLE LEFT", "THE TOWN IS STILL EMPTY", WHITE)


SEGMENTS = [
    Seg(["At one twenty three in the morning, a test at Chernobyl went wrong.",
         "The crazy part? It was a safety test."], d_gancho, {"title": "WHY DID CHERNOBYL EXPLODE?"}, tail=0.2),
    Seg(["If the power failed, backup generators needed a minute to start. Could the spinning turbine keep the cooling pumps running until then?"],
        d_teste, {"big": "THE TEST", "color": YELLOW}, tail=0.2),
    Seg(["The power dropped too low, so the operators pulled out almost every control rod, the reactor's brakes."],
        d_barras, {"big": "NO BRAKES", "color": PINK}, tail=0.2),
    Seg(["And this reactor had a flaw: more steam meant more power, which meant more steam."], d_vapor,
        {"big": "THE LOOP", "color": LARANJA}, tail=0.2),
    Seg(["They hit the emergency button. But the rods' tips pushed water out first, and the power spiked a hundred times."],
        d_botao, {"big": "THE BUTTON", "color": (1.0, 0.3, 0.25)}, tail=0.1, sfx=[(0, 0.0, "tick")]),
    Seg(["Seconds later, two explosions threw the thousand ton lid off the reactor."], d_explode,
        {"big": "BOOM", "color": (1.0, 0.3, 0.25)}, tail=0.3, sfx=[(0, 0.0, "whoosh")]),
    Seg(["The nearby town was evacuated the next day. Almost forty years later, it's still empty."], d_cidade,
        {"big": "GHOST TOWN", "color": WHITE}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Would you visit Chernobyl today?", "WOULD YOU VISIT IT?",
                                fundo=lambda ctx, t, s: (noite(ctx), usina(ctx, t))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
