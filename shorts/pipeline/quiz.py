"""Shared pieces of the interactive (quiz) format: question header, 3-2-1 ring timer, answer pill."""
import math

from core import BLUE, PINK, WHITE, Seg, pill, ramp, text_center

COUNT = 3.0  # seconds of countdown after each question


def head(q, n, sub):
    return {"big": f"QUESTION {q}", "big_size": 96, "sub": sub, "dots": ([str(i + 1) for i in range(n)], q - 1),
            "color": PINK if q == n else BLUE}


def countdown(ctx, t, start, cx=540, cy=1300):
    lt = t - start
    if not 0 <= lt < COUNT:
        return
    n = 3 - int(lt)
    frac = lt % 1
    ctx.set_source_rgba(0.04, 0.05, 0.09, 0.85)
    ctx.arc(cx, cy, 80, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_line_width(12)
    ctx.set_source_rgba(1, 1, 1, 0.15)
    ctx.arc(cx, cy, 62, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_source_rgb(*BLUE)
    ctx.arc(cx, cy, 62, -math.pi / 2, -math.pi / 2 + 2 * math.pi * (1 - frac))
    ctx.stroke()
    text_center(ctx, str(n), cx, cy + 26, 72, WHITE, "ExtraBold")


def answer(ctx, t, r, text, color, cy=1300):
    pill(ctx, text, 540, cy, color, ramp(t, r + 0.4, 0.3))


def question(q, n, sub, ask, reveal, draw, result_sfx="ding"):
    """Seg items: 0 = question line, 1 = countdown pause, 2 = reveal line."""
    return Seg([ask, COUNT, reveal], draw, head(q, n, sub),
               sfx=[(1, 0, "tick"), (1, 1, "tick"), (1, 2, "tick"), (2, 0.4, result_sfx)])
