"""Guess how many balls fill each container (3 rounds). Sun 01/11/2026, topic: satisfying rankings, format:
interactive. The balls are simulated (satisfying.fill_sim) and the answer is the simulated count."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import satisfying as sa  # noqa: E402
from core import GREEN, WHITE, YELLOW, Seg, pill, ramp, render, text_center  # noqa: E402
from quiz import COUNT, countdown, head  # noqa: E402

N = 3
FILL = 6.2
RODADAS = []
for forma, r, n_max, cor in (("copo", 44, 88, (0.36, 0.78, 0.98)), ("taca", 40, 79, (1.0, 0.36, 0.54)),
                             ("funil", 42, 68, (0.30, 0.90, 0.50))):
    sim = sa.fill_sim(forma, r, n_max, dur=FILL)  # n_max já é a capacidade: toda bola solta fica dentro
    assert sim[1] == len(sim[0][-1]) == n_max, (forma, sim[1], len(sim[0][-1]))
    RODADAS.append((sim, r, cor))


def rodada(sim, r, cor, opcoes):
    certo = str(sim[1])

    def draw(ctx, t, s):
        enchendo = t >= s.mark(2)
        lt = t - s.mark(2)
        sa.draw_fill(ctx, lt if enchendo else 0, sim, r, mostrar=enchendo, cor=cor)
        if not enchendo:  # uma bola de amostra, para ter noção do tamanho
            from physics import ball
            ball(ctx, sa.CX, sa.Y0 + 70, r - 1, cor)
            text_center(ctx, "1 BALL", sa.CX + r + 80, sa.Y0 + 82, 30, WHITE, "Bold", alpha=ramp(t, 0.2, 0.3))
        else:
            f = min(len(sim[0]) - 1, int(lt * 30))
            topo, fundo = sim[2][0], sim[2][1]
            ys = sim[0][f][:, 1] if len(sim[0][f]) else []
            dentro = int(((ys > topo - r) & (ys < fundo)).sum()) if len(ys) else 0
            text_center(ctx, str(dentro), sa.X1 - 120, sa.Y0 + 110, 84, YELLOW, "ExtraBold")
        rev = s.mark(3)
        for i, op in enumerate(opcoes):
            x = sa.CX + (i - 1) * 300
            c = (GREEN if op == certo else (0.35, 0.37, 0.42)) if t >= rev else WHITE
            pill(ctx, f"{'ABC'[i]}. {op}", x, sa.Y1 - 50, c, ramp(t, 0.3 + 0.15 * i, 0.3), size=40)
        countdown(ctx, t, s.mark(1), cx=sa.X1 - 120, cy=sa.Y0 + 110)
    return draw


def pergunta(q, sub, ask, opcoes, reveal):
    sim, r, cor = RODADAS[q - 1]
    assert str(sim[1]) in opcoes, (sim[1], opcoes)
    return Seg([ask, COUNT, FILL, reveal], rodada(sim, r, cor, opcoes), head(q, N, sub),
               sfx=[(1, 0, "tick"), (1, 1, "tick"), (1, 2, "tick"), (3, 0.1, "ding")], tail=0.5)


def d_intro(ctx, t, s):
    sim, r, cor = RODADAS[0]
    sa.draw_fill(ctx, t + 1.5, sim, r, cor=None)


SEGMENTS = [
    Seg(["Guess how many balls it takes to fill each container. Three rounds."], d_intro,
        {"title": "GUESS HOW MANY BALLS FILL IT"}, tail=0.3),
    pergunta(1, "THE GLASS", "Round one. How many balls fill this glass?", ["60", str(RODADAS[0][0][1]), "120"],
             f"{RODADAS[0][0][1]} balls!"),
    pergunta(2, "THE BOWL", "Round two. A round bowl, with smaller balls.",
             [str(RODADAS[1][0][1]), "55", "110"], f"{RODADAS[1][0][1]}! The curve hides a lot of space."),
    pergunta(3, "THE FUNNEL", "Last one. A funnel. Careful, it narrows fast.",
             ["100", "45", str(RODADAS[2][0][1])], f"{RODADAS[2][0][1]}. Did you get it?"),
    Seg(["How many did you get right? Comment your score!"], d_intro, {"title": "HOW MANY DID YOU GET?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
