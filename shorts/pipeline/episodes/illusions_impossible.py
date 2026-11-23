"""5 impossible shapes that break your brain, ranked (#5 -> #1). Mon 09/11/2026, topic: optical illusions, format:
ranking. Search 08/11: "optical illusion", median 2.4M views (last 30 days).

Items (all drawn by code):
- #5 Necker cube (Louis Necker, 1832): a wireframe cube that flips between two 3D readings;
- #4 Schroeder stairs (Heinrich Schroeder, 1858): stairs seen from above or from below;
- #3 Devil's fork / blivet (1960s): three round prongs on one end, two square prongs on the other;
- #2 Reutersvard triangle (Oscar Reutersvard, 1934): the first impossible triangle, drawn with cubes;
- #1 Penrose triangle (Lionel and Roger Penrose, 1958): looks like one closed solid; turned, it is three separate
  bars that only line up from one viewpoint (that is how real "impossible triangle" sculptures are built).
The cube figures use a true 3D projection: at the isometric angle the end cube (4,4,4) lands exactly on (0,0,0).
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2 + 20
DOTS = ["5", "4", "3", "2", "1"]
FUNDO = (0.08, 0.10, 0.16)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def painel(ctx):
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source_rgb(*FUNDO)
    ctx.fill()


# ---------------- cubos em 3D (Reutersvärd e Penrose) ----------------

def proj(p, az, el=math.radians(35.264), s=60.0, c=(CX, CY)):
    x, y, z = p
    ca, sa = math.cos(az), math.sin(az)
    xr, yr = x * ca - y * sa, x * sa + y * ca
    ce, se = math.cos(el), math.sin(el)
    return c[0] + s * xr, c[1] - s * (z * ce - yr * se)  # yr positivo = longe


def caminho(n):
    """Cubos ao longo de x, depois y, depois z: o último fica logo abaixo de (n,n,n), que na isométrica = (0,0,0)."""
    cs = [(i, 0, 0) for i in range(n + 1)] + [(n, j, 0) for j in range(1, n + 1)] + [(n, n, k) for k in range(1, n)]
    return cs


CORES = {"z": (0.98, 0.84, 0.35), "x": (0.36, 0.70, 0.98), "y": (0.95, 0.40, 0.55)}


def cubos(ctx, cs, az, s, centro, contorno=True, primeiro_por_cima=True):
    """Desenha cubos unitários (pintor: do mais longe para o mais perto). Na vista isométrica o primeiro cubo é
    desenhado por último: é esse truque que fecha o triângulo impossível."""
    vx, vy = math.sin(az) * math.cos(0.6155), math.cos(az) * math.cos(0.6155)
    meio = np.mean(np.array(cs, float), axis=0)
    pts = [(c[0] - meio[0], c[1] - meio[1], c[2] - meio[2]) for c in cs]

    def prof(p):
        return p[0] * vx + p[1] * vy + p[2] * 0.577
    ordem = sorted(range(len(pts)), key=lambda i: prof(pts[i]))
    if primeiro_por_cima and abs(az - math.radians(45)) < 0.03:
        ordem.remove(0)
        ordem.append(0)
    for i in ordem:
        x, y, z = pts[i]
        faces = [
            ("z", [(x, y, z + 1), (x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)]),
            ("x", [(x + 1, y, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x + 1, y, z + 1)]) if vx > 0 else
            ("x", [(x, y, z), (x, y + 1, z), (x, y + 1, z + 1), (x, y, z + 1)]),
            ("y", [(x, y + 1, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)]) if vy > 0 else
            ("y", [(x, y, z), (x + 1, y, z), (x + 1, y, z + 1), (x, y, z + 1)]),
        ]
        for eixo, quad in faces:
            q = [proj(p, az, s=s, c=centro) for p in quad]
            ctx.move_to(*q[0])
            for p in q[1:]:
                ctx.line_to(*p)
            ctx.close_path()
            ctx.set_source_rgb(*CORES[eixo])
            if contorno:
                ctx.fill_preserve()
                ctx.set_source_rgb(*FUNDO)
                ctx.set_line_width(3)
                ctx.stroke()
            else:
                ctx.fill_preserve()
                ctx.set_line_width(1.2)
                ctx.stroke()


# ---------------- figuras em 2D ----------------

def necker(ctx, t, s):
    """Cubo de arame; a face "da frente" alterna (destaque) para mostrar as duas leituras."""
    a = 230
    d = 120
    f = [(CX - a / 2 - d / 2, CY - a / 2 + d / 2 + 40), (CX + a / 2 - d / 2, CY - a / 2 + d / 2 + 40),
         (CX + a / 2 - d / 2, CY + a / 2 + d / 2 + 40), (CX - a / 2 - d / 2, CY + a / 2 + d / 2 + 40)]
    b = [(x + d, y - d) for x, y in f]
    k = s.mark(1) if len(s.items) > 1 else 1.0
    lado = int(max(0.0, t - k) / 1.0) % 2 if t > k else -1
    for face, ativo in ((f, lado == 0), (b, lado == 1)):
        if ativo:
            ctx.move_to(*face[0])
            for p in face[1:]:
                ctx.line_to(*p)
            ctx.close_path()
            ctx.set_source_rgba(*YELLOW, 0.35)
            ctx.fill()
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(7)
    ctx.set_line_join(1)
    for face in (f, b):
        ctx.move_to(*face[0])
        for p in face[1:]:
            ctx.line_to(*p)
        ctx.close_path()
        ctx.stroke()
    for p, q in zip(f, b):
        ctx.move_to(*p)
        ctx.line_to(*q)
    ctx.stroke()
    if lado >= 0:
        text_center(ctx, "FRONT FACE: " + ("BOTTOM-LEFT" if lado == 0 else "TOP-RIGHT"), CX, Y1 - 70, 30, YELLOW, "Bold")


def schroder(ctx, t, s):
    """Escada de Schröder (feita de cubos): girada 180°, continua sendo uma escada, vista de baixo."""
    cs = [(i, 0, k) for i in range(5) for k in range(i + 1)] + [(i, 1, k) for i in range(5) for k in range(i + 1)]
    vira = ease((t - s.mark(1)) / 0.9) if len(s.items) > 1 else 0.0
    ctx.save()
    ctx.translate(CX, CY + 20)
    ctx.rotate(math.pi * vira)
    ctx.translate(-CX, -(CY + 20))
    cubos(ctx, cs, math.radians(45), 72, (CX, CY + 20), primeiro_por_cima=False)
    ctx.restore()


def blivet(ctx, t, s):
    """Garfo do diabo: 3 pontas redondas à esquerda, 2 retangulares à direita, com as mesmas linhas."""
    ys = [-150, -80, -35, 35, 80, 150]
    xa, xm, xb = X0 + 110, CX + 20, X1 - 90
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(7)
    for k in range(3):  # pontas redondas
        y1, y2 = ys[2 * k], ys[2 * k + 1]
        cy = CY + (y1 + y2) / 2
        ctx.save()
        ctx.translate(xa, cy)
        ctx.scale(16, (y2 - y1) / 2)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.stroke()
    for y in ys:  # as 6 linhas vão até o meio
        ctx.move_to(xa, CY + y)
        ctx.line_to(xm, CY + y)
    ctx.stroke()
    for y in (-150, 150, -35, 35):  # do meio em diante, só 4 linhas: 2 barras
        ctx.move_to(xm if abs(y) == 150 else xm - 40, CY + y)
        ctx.line_to(xb, CY + y)
    ctx.stroke()
    ctx.move_to(xm - 40, CY - 35)
    ctx.curve_to(xm - 90, CY - 30, xm - 90, CY + 30, xm - 40, CY + 35)
    ctx.stroke()
    for y1, y2 in ((-150, -35), (35, 150)):
        ctx.move_to(xb, CY + y1)
        ctx.line_to(xb, CY + y2)
    ctx.stroke()
    if len(s.items) > 1 and t > s.mark(1):
        a = ramp(t, s.mark(1), 0.3)
        text_center(ctx, "3 ROUND", xa + 10, CY + 230, 34, YELLOW, "ExtraBold", alpha=a)
        text_center(ctx, "2 SQUARE", xb - 70, CY + 230, 34, YELLOW, "ExtraBold", alpha=a)


def reutersvard(ctx, t, s):
    cubos(ctx, caminho(3), math.radians(45), 100, (CX, CY + 40))
    text_center(ctx, "OSCAR REUTERSVÄRD, 1934", CX, Y1 - 60, 28, WHITE, "SemiBold",
              alpha=ramp(t, s.mark(1) if len(s.items) > 1 else 1.0, 0.3))


def penrose(ctx, t, s):
    """Triângulo de Penrose; depois da 2ª frase, a vista gira e ele se separa em três barras."""
    k = s.mark(1) if len(s.items) > 1 else 99
    gira = ease((t - k) / 1.6)
    az = math.radians(45 + 32 * gira)
    cubos(ctx, caminho(5), az, 74, (CX, CY + 30), contorno=False)
    if gira > 0.9:
        text_center(ctx, "3 SEPARATE BARS", CX, Y1 - 60, 34, YELLOW, "ExtraBold", alpha=ramp(t, k + 1.5, 0.3))


def cena(fig):
    def draw(ctx, t, s):
        painel(ctx)
        fig(ctx, t, s)
    return draw


def d_intro(ctx, t, s):
    painel(ctx)
    cubos(ctx, caminho(5), math.radians(45 + 6 * math.sin(t * 2.2) * (1 - ease(t / 2.5))), 74, (CX, CY + 30),
          contorno=False)


SEGMENTS = [
    Seg(["Five shapes that can't exist. Number one breaks on camera."], d_intro,
        {"title": "5 IMPOSSIBLE SHAPES"}, tail=0.2),
    Seg(["Number five, the Necker cube.", "Stare at it, and it flips inside out."],
        cena(necker), head(5, "NECKER CUBE"), sfx=[(1, 0, "ding")]),
    Seg(["Number four, Schroeder's stairs.", "Turn them upside down. Still stairs."],
        cena(schroder), head(4, "SCHROEDER STAIRS"), sfx=[(1, 0, "whoosh")]),
    Seg(["Number three, the devil's fork.", "Count the prongs. Three round ones become two square ones."],
        cena(blivet), head(3, "DEVIL'S FORK"), sfx=[(1, 0, "ding")]),
    Seg(["Number two, the first impossible triangle,", "drawn with cubes back in nineteen thirty four."],
        cena(reutersvard), head(2, "REUTERSVÄRD TRIANGLE"), sfx=[(1, 0, "ding")]),
    Seg(["And number one, the Penrose triangle.", "Turn it, and it's just three bars lined up perfectly."],
        cena(penrose), head(1, "PENROSE TRIANGLE"), sfx=[(1, 0, "whoosh")], tail=0.8),
]
SEGMENTS.append(pq.seg_pergunta("Which one broke your brain?", "WHICH ONE BROKE YOUR BRAIN?",
                                fundo=lambda ctx, t, s: d_intro(ctx, 9.0, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
