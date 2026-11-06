"""The 5 biggest animals alive, to scale next to a human (#5 -> #1, by weight). Sat 07/11/2026, topic: size and
scale, format: ranking. Search 06/11: "biggest animals size comparison", median 106k views (last 30 days).

Facts (adult maximums commonly cited):
- giraffe: up to ~5.8 m tall, males up to ~1.9 t;
- common hippopotamus: large males up to ~4.5 t; can sprint ~30 km/h on land (faster than most people);
- African bush elephant: adult bulls about 6 t, shoulder ~3.2 m, heaviest land animal;
- whale shark: a fish (a shark), not a whale; up to ~18 m long and ~20 t, the biggest fish alive;
- blue whale: up to ~30 m long and ~190 t, the heaviest animal known to have ever lived.
Silhouettes are stylised, drawn by code at true relative size (human = 1.8 m).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, GRAY, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CHAO = Y1 - 190
DOTS = ["5", "4", "3", "2", "1"]
FUNDO_A, FUNDO_B = (0.10, 0.20, 0.33), (0.04, 0.08, 0.15)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def cenario(ctx, ppm):
    import cairo
    g = cairo.LinearGradient(0, Y0, 0, Y1)
    g.add_color_stop_rgb(0, *FUNDO_A)
    g.add_color_stop_rgb(1, *FUNDO_B)
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source(g)
    ctx.fill()
    passo = 1 if ppm > 90 else (2 if ppm > 45 else 5)  # régua no chão
    m = 0
    while X0 + 60 + m * ppm < X1 - 30:
        x = X0 + 60 + m * ppm
        ctx.set_source_rgba(1, 1, 1, 0.35)
        ctx.rectangle(x - 1, CHAO, 2, 16)
        ctx.fill()
        text_center(ctx, f"{m} m", x, CHAO + 46, 20, GRAY, "SemiBold")
        m += passo
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.rectangle(X0 + 30, CHAO, X1 - X0 - 60, 3)
    ctx.fill()


def em_metros(ctx, x0, ppm):
    """Sistema de coordenadas em metros: x para a direita, y para cima a partir do chão."""
    ctx.save()
    ctx.translate(x0, CHAO)
    ctx.scale(ppm, -ppm)


def elipse(ctx, cx, cy, rx, ry):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def humano(ctx, x0, ppm):
    em_metros(ctx, x0, ppm)
    ctx.set_source_rgb(*BLUE)
    elipse(ctx, 0.25, 1.66, 0.12, 0.13)
    ctx.fill()
    ctx.move_to(0.08, 1.5)
    ctx.line_to(0.42, 1.5)
    ctx.line_to(0.38, 0.85)
    ctx.line_to(0.34, 0.0)
    ctx.line_to(0.27, 0.0)
    ctx.line_to(0.25, 0.8)
    ctx.line_to(0.23, 0.0)
    ctx.line_to(0.16, 0.0)
    ctx.line_to(0.12, 0.85)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def girafa(ctx):
    cor, mancha = (0.88, 0.64, 0.30), (0.55, 0.33, 0.14)
    ctx.set_source_rgb(*cor)
    for x in (1.05, 1.35, 2.55, 2.85):
        ctx.rectangle(x, 0, 0.13, 2.0)
    elipse(ctx, 2.0, 2.3, 1.15, 0.55)
    ctx.move_to(2.75, 2.55)
    ctx.line_to(3.15, 2.2)
    ctx.line_to(4.05, 5.15)
    ctx.line_to(3.7, 5.35)
    ctx.close_path()
    elipse(ctx, 4.05, 5.35, 0.38, 0.16)
    ctx.fill()
    ctx.set_source_rgb(*mancha)
    for cx, cy in ((1.4, 2.4), (1.9, 2.2), (2.4, 2.45), (1.7, 2.6), (2.25, 2.0), (3.2, 3.0), (3.45, 3.8), (3.7, 4.6)):
        elipse(ctx, cx, cy, 0.14, 0.1)
    ctx.rectangle(3.85, 5.45, 0.05, 0.35)
    ctx.rectangle(3.98, 5.45, 0.05, 0.35)
    ctx.fill()
    ctx.set_line_width(0.06)
    ctx.move_to(0.88, 2.4)
    ctx.line_to(0.7, 1.4)
    ctx.stroke()


def hipopotamo(ctx):
    ctx.set_source_rgb(0.55, 0.47, 0.56)
    for x in (0.9, 1.3, 2.6, 3.0):
        ctx.rectangle(x, 0, 0.32, 0.6)
    elipse(ctx, 2.0, 0.95, 1.75, 0.7)
    elipse(ctx, 3.85, 1.05, 0.7, 0.45)
    elipse(ctx, 4.35, 0.92, 0.45, 0.38)
    ctx.fill()
    ctx.set_source_rgb(0.42, 0.35, 0.43)
    elipse(ctx, 3.55, 1.48, 0.1, 0.08)
    ctx.fill()


def elefante(ctx):
    ctx.set_source_rgb(0.62, 0.62, 0.66)
    for x in (0.9, 1.5, 3.0, 3.55):
        ctx.rectangle(x, 0, 0.5, 1.6)
    elipse(ctx, 2.4, 2.25, 1.75, 1.05)
    elipse(ctx, 4.25, 2.65, 0.78, 0.75)
    ctx.fill()
    ctx.set_line_width(0.34)
    ctx.set_line_cap(1)
    ctx.move_to(4.75, 2.3)
    ctx.curve_to(5.05, 1.6, 4.95, 0.8, 5.15, 0.25)
    ctx.stroke()
    ctx.set_source_rgb(0.5, 0.5, 0.55)
    elipse(ctx, 3.85, 2.45, 0.5, 0.8)
    ctx.fill()
    ctx.set_source_rgb(0.97, 0.95, 0.88)
    ctx.set_line_width(0.12)
    ctx.move_to(4.7, 2.05)
    ctx.curve_to(5.0, 1.75, 5.25, 1.75, 5.45, 1.95)
    ctx.stroke()


def tubarao_baleia(ctx):
    L = 18.0
    ctx.set_source_rgb(0.25, 0.36, 0.5)
    ctx.move_to(0, 1.4)
    ctx.curve_to(0.2, 2.6, 4, 3.3, 8, 3.0)
    ctx.curve_to(12, 2.6, 14, 1.9, L - 2.6, 1.6)
    ctx.line_to(L, 4.2)
    ctx.line_to(L - 1.5, 1.2)
    ctx.line_to(L - 0.4, -0.2 + 0.4)
    ctx.line_to(L - 2.8, 0.95)
    ctx.curve_to(13, 0.4, 6, 0.2, 2, 0.35)
    ctx.curve_to(0.8, 0.45, 0.05, 0.8, 0, 1.4)
    ctx.close_path()
    ctx.move_to(7.5, 2.95)
    ctx.line_to(9.0, 4.4)
    ctx.line_to(10.0, 2.8)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(0.92, 0.95, 1.0)
    for i in range(46):
        cx = 1.5 + (i * 3.7) % 12.5
        cy = 0.9 + ((i * 1.3) % 1.9)
        elipse(ctx, cx, cy, 0.09, 0.09)
    ctx.fill()


def baleia_azul(ctx):
    L = 30.0
    ctx.set_source_rgb(0.30, 0.45, 0.66)
    ctx.move_to(0, 1.3)
    ctx.curve_to(0.5, 3.6, 8, 4.3, 14, 3.8)
    ctx.curve_to(20, 3.3, 24, 2.2, L - 2.2, 1.7)
    ctx.line_to(L, 2.5)
    ctx.line_to(L - 0.4, 1.4)
    ctx.line_to(L, 0.4)
    ctx.line_to(L - 2.2, 1.2)
    ctx.curve_to(22, 0.3, 12, 0.0, 4, 0.3)
    ctx.curve_to(1.5, 0.45, 0.1, 0.7, 0, 1.3)
    ctx.close_path()
    ctx.move_to(21.5, 2.9)
    ctx.line_to(22.6, 3.5)
    ctx.line_to(23.0, 2.6)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.25)  # pregas da garganta
    ctx.set_line_width(0.08)
    for k in range(4):
        ctx.move_to(1.0, 0.55 + k * 0.18)
        ctx.curve_to(4, 0.35 + k * 0.18, 7, 0.4 + k * 0.18, 9, 0.6 + k * 0.15)
    ctx.stroke()
    ctx.set_source_rgb(0.1, 0.12, 0.2)
    elipse(ctx, 2.4, 1.6, 0.14, 0.12)
    ctx.fill()


ANIMAIS = {  # desenho, comprimento (m), altura (m), toneladas
    "girafa": (girafa, 4.5, 5.8, 1.9),
    "hipopotamo": (hipopotamo, 4.8, 1.6, 4.5),
    "elefante": (elefante, 5.6, 3.4, 6.0),
    "tubarao": (tubarao_baleia, 18.0, 4.4, 20.0),
    "baleia": (baleia_azul, 30.0, 4.3, 190.0),
}


def animal(ctx, nome, x0, ppm, k=1.0):
    """Desenha o animal em escala; k (0..1) faz ele entrar deslizando da direita."""
    desenho, comp, alt, _ = ANIMAIS[nome]
    dx = (1 - ease(k)) * (X1 - X0)
    em_metros(ctx, x0 + dx, ppm)
    desenho(ctx)
    ctx.restore()


def ppm_para(nome):
    _, comp, alt, _ = ANIMAIS[nome]
    return min((X1 - X0 - 230) / comp, 470 / alt)


def cena(nome, nota, cor):
    _, comp, alt, ton = ANIMAIS[nome]
    ppm = ppm_para(nome)

    def draw(ctx, t, s):
        cenario(ctx, ppm)
        humano(ctx, X0 + 60, ppm)
        animal(ctx, nome, X0 + 60 + 0.8 * ppm + 20, ppm, ramp(t, 0.1, 1.0))
        k = ease((t - s.mark(1)) / 1.3)
        a = ramp(t, s.mark(1), 0.3)
        txt = f"{ton * k:.1f} TONNES" if ton < 10 else f"{ton * k:,.0f} TONNES"
        text_center(ctx, txt, (X0 + X1) / 2, Y0 + 75, 66, cor, "ExtraBold", alpha=a)
        text_center(ctx, nota, (X0 + X1) / 2, Y0 + 125, 32, WHITE, "Bold", alpha=ramp(t, s.mark(1) + 1.2, 0.3))
        text_center(ctx, "YOU (1.8 m)", X0 + 60 + 0.25 * ppm, CHAO - 1.8 * ppm - 24, 22, BLUE, "Bold")
    return draw


def fila(ctx, t, s=None, k0=0.2):
    """Os cinco em escala lado a lado (escala da baleia): a baleia azul engole a cena."""
    ppm = (X1 - X0 - 120) / 30.0
    cenario(ctx, ppm)
    humano(ctx, X0 + 60, ppm)
    x = X0 + 60 + 0.8 * ppm
    for i, nome in enumerate(("girafa", "hipopotamo", "elefante")):
        animal(ctx, nome, x, ppm, ramp(t, k0 + i * 0.25, 0.7))
        x += ANIMAIS[nome][1] * ppm + 8
    for nome, alto, k in (("tubarao", 6.5, 0.8), ("baleia", 11.8, 1.2)):  # os do mar "nadam" acima dos outros
        if t > k0 + k:
            ctx.save()
            ctx.translate(0, -alto * ppm)
            animal(ctx, nome, X0 + 60, ppm, ramp(t, k0 + k, 0.9))
            ctx.restore()


def d_intro(ctx, t, s):
    fila(ctx, t, s, 0.0)


SEGMENTS = [
    Seg(["The five biggest animals alive, to scale next to you."], d_intro,
        {"title": "THE BIGGEST ANIMALS, TO SCALE"}, tail=0.3),
    Seg(["Number five, the giraffe.", "Almost six meters tall, and up to two tonnes."],
        cena("girafa", "5.8 m TALL", YELLOW), head(5, "GIRAFFE"), sfx=[(1, 1.3, "ding")]),
    Seg(["Number four, the hippo.", "Up to four and a half tonnes, and it can outrun you."],
        cena("hipopotamo", "FASTER THAN YOU ON LAND", YELLOW), head(4, "HIPPOPOTAMUS"), sfx=[(1, 1.3, "ding")]),
    Seg(["Number three, the African elephant.", "About six tonnes, the heaviest animal on land."],
        cena("elefante", "HEAVIEST ON LAND", YELLOW), head(3, "AFRICAN ELEPHANT"), sfx=[(1, 1.3, "ding")]),
    Seg(["Number two looks like a whale, but it's a shark!", "The whale shark, eighteen meters long, the biggest fish alive."],
        cena("tubarao", "IT'S A FISH, NOT A WHALE", YELLOW), head(2, "WHALE SHARK"), sfx=[(1, 1.3, "ding")]),
    Seg(["And number one, the blue whale.", "Thirty meters, up to one hundred ninety tonnes. The heaviest animal ever."],
        cena("baleia", "HEAVIEST ANIMAL EVER", PINK), head(1, "BLUE WHALE"), sfx=[(1, 1.3, "ding")], tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Which one would you want to see up close?", "WHICH ONE UP CLOSE?",
                                fundo=lambda ctx, t, s: fila(ctx, 9.0)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
