"""Same colour or not? 4-question quiz. Tuesday 27/10/2026, topic: optical illusions, format: interactive."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import illusions as il  # noqa: E402
from core import BLUE, GREEN, RED, PINK, WHITE, Seg, ramp, render, pill, text_center  # noqa: E402

DOTS = ["1", "2", "3", "4"]
COUNT = 3.0  # seconds of countdown after each question


def head(q, sub):
    return {"big": f"QUESTION {q}", "big_size": 96, "sub": sub, "dots": (DOTS, q - 1),
            "color": PINK if q == 4 else BLUE}


def countdown(ctx, t, start):
    """Ring timer 3-2-1 between the question and the answer."""
    lt = t - start
    if not 0 <= lt < COUNT:
        return
    n = 3 - int(lt)
    frac = lt % 1
    ctx.set_source_rgba(0.04, 0.05, 0.09, 0.85)
    ctx.arc(540, 1300, 80, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_line_width(12)
    ctx.set_source_rgba(1, 1, 1, 0.15)
    ctx.arc(540, 1300, 62, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_source_rgb(*BLUE)
    ctx.arc(540, 1300, 62, -math.pi / 2, -math.pi / 2 + 2 * math.pi * (1 - frac))
    ctx.stroke()
    text_center(ctx, str(n), 540, 1326, 72, WHITE, "ExtraBold")


def answer(ctx, t, r, text, color):
    pill(ctx, text, 540, 1300, color, ramp(t, r + 0.4, 0.3))


def d_intro(ctx, t, s):
    ctx.save()
    il.gradient_squares(ctx, 0.5, 0.5)
    ctx.restore()


def d1(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.gradient_squares(ctx, 0.5, 0.5, bridge=ramp(t, r, 0.8), flatten=ramp(t, r + 1.2, 0.8))
    ctx.restore()
    countdown(ctx, t, s.mark(1))
    answer(ctx, t, r, "SAME GRAY", GREEN)


def d2(ctx, t, s):
    r = s.mark(2)
    il.whites(ctx, flatten=ramp(t, r, 0.9))
    countdown(ctx, t, s.mark(1))
    answer(ctx, t, r, "SAME GRAY", GREEN)


def d3(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.gradient_squares(ctx, 0.40, 0.58, flatten=ramp(t, r, 0.9))
    ctx.restore()
    countdown(ctx, t, s.mark(1))
    answer(ctx, t, r, "DIFFERENT!", RED)


def d4(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.munker(ctx, fade=ramp(t, r, 0.9))
    ctx.restore()
    countdown(ctx, t, s.mark(1))
    answer(ctx, t, r, "SAME RED", GREEN)


def d_outro(ctx, t, s):
    ctx.save()
    il.gradient_squares(ctx, 0.5, 0.5)
    ctx.restore()


def q(n, sub, question, reveal, draw, result_sfx="ding"):
    return Seg([question, COUNT, reveal], draw, head(n, sub),
               sfx=[(1, 0, "tick"), (1, 1, "tick"), (1, 2, "tick"), (2, 0.4, result_sfx)])


SEGMENTS = [
    Seg(["Your eyes are lying to you. Four color tests. Keep score!"], d_intro,
        {"title": "SAME COLOR OR NOT?"}, tail=0.3),
    q(1, "WHICH SQUARE IS LIGHTER?", "Question one. Which square is lighter, left or right?",
      "They're the exact same gray. The background fools you.", d1),
    q(2, "LEFT BARS OR RIGHT BARS?", "Question two. Which gray bars are lighter?",
      "Same gray again! The stripes around them change what you see.", d2),
    q(3, "SAME COLOR THIS TIME?", "Question three. These two look about the same, right?",
      "Gotcha! This time they really are different. The right one is lighter.", d3),
    q(4, "PURPLE OR ORANGE?", "Last one. The left red looks purple, the right looks orange.",
      "It's the same red! Only the stripes on top are different.", d4),
    Seg(["How many did you get right? Comment your score!"], d_outro,
        {"title": "HOW MANY DID YOU GET RIGHT?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
