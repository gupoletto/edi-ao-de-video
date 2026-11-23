"""The 5 biggest stars, to scale (#5 -> #1). Wed 11/11/2026, topic: space, format: ranking.
Search 11/11: "biggest stars size comparison", median 274k views (last 30 days).

Radii in solar radii (R_sun = 696,000 km; 1 AU = 215 R_sun). Published estimates vary, most for the red supergiants:
- Sirius A ~1.71 (nearly twice as wide as the Sun);
- Rigel ~79 -> 0.37 AU, almost Mercury's orbit (0.39 AU);
- Betelgeuse ~760 (estimates ~640-1,000) -> ~3.5 AU, past Mars (1.52 AU) and the asteroid belt (2.2-3.3 AU);
- VY Canis Majoris ~1,420 -> ~6.6 AU, past Jupiter's orbit (5.2 AU);
- Stephenson 2-18 ~2,150 (uncertain; among the largest known) -> ~10 AU, about Saturn's orbit (9.5 AU).
The animation zooms out between stars on a log scale; each star is drawn at true size relative to the previous one.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2 + 60
RAIO_TELA = 300          # raio (px) do astro em destaque
DOTS = ["5", "4", "3", "2", "1"]
AU = 215.0
ESTRELAS = {  # raio (R_sol), cor do centro, cor da borda
    "sol": (1.0, (1.0, 0.95, 0.7), (1.0, 0.75, 0.25)),
    "sirius": (1.71, (1.0, 1.0, 1.0), (0.70, 0.82, 1.0)),
    "rigel": (79.0, (0.92, 0.96, 1.0), (0.45, 0.62, 1.0)),
    "betelgeuse": (760.0, (1.0, 0.75, 0.45), (0.85, 0.30, 0.12)),
    "vycma": (1420.0, (1.0, 0.62, 0.40), (0.70, 0.18, 0.10)),
    "stephenson": (2150.0, (1.0, 0.55, 0.35), (0.60, 0.12, 0.10)),
}
ORDEM = ["sol", "sirius", "rigel", "betelgeuse", "vycma", "stephenson"]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def ceu(ctx):
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source_rgb(0.02, 0.02, 0.05)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.7)
    for i in range(90):
        x = X0 + (i * 397) % (X1 - X0)
        y = Y0 + (i * 211) % (Y1 - Y0)
        ctx.arc(x, y, 1.2 + (i % 3) * 0.6, 0, 2 * math.pi)
        ctx.fill()


def estrela(ctx, x, y, r, nome, t=0.0):
    import cairo
    if r < 0.6:
        ctx.set_source_rgb(*ESTRELAS[nome][2])
        ctx.arc(x, y, 1.5, 0, 2 * math.pi)
        ctx.fill()
        return
    _, c0, c1 = ESTRELAS[nome]
    g = cairo.RadialGradient(x - r * 0.25, y - r * 0.25, r * 0.05, x, y, r)
    g.add_color_stop_rgb(0, *c0)
    g.add_color_stop_rgb(1, *c1)
    ctx.arc(x, y, r * (1 + 0.006 * math.sin(t * 3)), 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    if r > 30:  # brilho em volta
        gg = cairo.RadialGradient(x, y, r, x, y, r * 1.18)
        gg.add_color_stop_rgba(0, *c1, 0.35)
        gg.add_color_stop_rgba(1, *c1, 0.0)
        ctx.arc(x, y, r * 1.18, 0, 2 * math.pi)
        ctx.set_source(gg)
        ctx.fill()


def orbita(ctx, r_px, rot, a=1.0):
    ctx.save()
    ctx.set_dash([10, 8])
    ctx.set_line_width(3)
    ctx.set_source_rgba(1, 1, 1, 0.85 * a)
    ctx.new_path()
    ctx.arc(CX, CY, r_px, 0, 2 * math.pi)
    ctx.stroke()
    ctx.restore()
    text_center(ctx, rot, CX, CY - r_px - 12, 26, WHITE, "Bold", alpha=a)


def cena(nome, orb=None, nota=""):
    i = ORDEM.index(nome)
    ant = ORDEM[i - 1]
    r_novo, r_ant = ESTRELAS[nome][0], ESTRELAS[ant][0]

    def draw(ctx, t, s):
        ctx.save()
        ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
        ctx.clip()
        ceu(ctx)
        z = ease((t - 0.2) / 1.3)  # zoom out: a anterior começa do tamanho da tela e encolhe até a escala real
        escala = RAIO_TELA / (r_ant * (r_novo / r_ant) ** z)   # px por R_sol
        rn, ra = r_novo * escala, r_ant * escala
        estrela(ctx, CX, CY, rn, nome, t)
        # a anterior, em escala, no canto de baixo à esquerda da nova (ou no centro enquanto é maior que o quadro)
        if z < 1:
            estrela(ctx, CX, CY, ra, ant, t) if rn < ra * 1.01 else None
        xa = CX - rn * 0.62 if rn > 40 else CX - 160
        estrela(ctx, xa, CY + rn * 0.78 if rn > 40 else CY, max(ra, 1.6), ant, t)
        text_center(ctx, f"{r_novo:,.0f}x THE SUN" if r_novo >= 10 else f"{r_novo:.1f}x THE SUN", CX, Y0 + 70, 56,
                    YELLOW, "ExtraBold", alpha=ramp(t, 1.3, 0.3))
        if orb and t > s.mark(1):
            nome_o, au = orb
            orbita(ctx, au * AU * escala, nome_o, ramp(t, s.mark(1), 0.4))
        if nota:
            text_center(ctx, nota, CX, Y1 - 40, 30, WHITE, "Bold", alpha=ramp(t, 1.6, 0.3))
        ctx.restore()
    return draw


def d_intro(ctx, t, s):
    ctx.save()
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.clip()
    ceu(ctx)
    k = min(4.999, t / 0.7)
    i = int(k)
    a, b = ORDEM[i + 1], ORDEM[min(5, i + 2)]
    f = k - i
    escala = RAIO_TELA / (ESTRELAS[a][0] * (ESTRELAS[b][0] / ESTRELAS[a][0]) ** f)
    for nome in reversed(ORDEM):
        r = ESTRELAS[nome][0] * escala
        if r < 6000:
            estrela(ctx, CX, CY + RAIO_TELA - r, r, nome, t)
    ctx.restore()


SEGMENTS = [
    Seg(["The biggest stars we know, to scale. Our Sun is a dot."], d_intro,
        {"title": "THE BIGGEST STARS, TO SCALE"}, tail=0.2),
    Seg(["Number five, Sirius, the brightest star in our sky.", "Almost twice as wide as the Sun."],
        cena("sirius", nota="BRIGHTEST STAR IN THE NIGHT SKY"), head(5, "SIRIUS A"), sfx=[(1, 0, "ding")]),
    Seg(["Number four, Rigel.", "Put it where the Sun is, and it almost reaches Mercury."],
        cena("rigel", orb=("MERCURY'S ORBIT", 0.39)), head(4, "RIGEL"), sfx=[(1, 0, "ding")]),
    Seg(["Number three, Betelgeuse.", "It would swallow Mercury, Venus, Earth and Mars."],
        cena("betelgeuse", orb=("MARS'S ORBIT", 1.52)), head(3, "BETELGEUSE"), sfx=[(1, 0, "ding")]),
    Seg(["Number two, VY Canis Majoris.", "Even Jupiter's orbit fits inside it."],
        cena("vycma", orb=("JUPITER'S ORBIT", 5.2)), head(2, "VY CANIS MAJORIS"), sfx=[(1, 0, "ding")]),
    Seg(["And number one, Stephenson two eighteen.", "About two thousand Suns wide. It reaches Saturn."],
        cena("stephenson", orb=("SATURN'S ORBIT", 9.5), nota="ESTIMATES VARY"), head(1, "STEPHENSON 2-18"),
        sfx=[(1, 0, "whoosh")], tail=0.7),
]
SEGMENTS.append(pq.seg_pergunta("Did you know the Sun was this tiny?", "DID YOU KNOW THE SUN WAS TINY?",
                                fundo=lambda ctx, t, s: cena("stephenson")(ctx, 3.0, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
