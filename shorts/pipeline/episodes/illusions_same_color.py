"""Same colour or not? 4-question quiz. Tuesday 27/10/2026, topic: optical illusions, format: interactive."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import illusions as il  # noqa: E402
from core import GREEN, RED, Seg, ramp, render  # noqa: E402
from quiz import answer, countdown, question  # noqa: E402

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


SEGMENTS = [
    Seg(["Your eyes are lying to you. Four color tests. Keep score!"], d_intro,
        {"title": "SAME COLOR OR NOT?"}, tail=0.3),
    question(1, 4, "WHICH SQUARE IS LIGHTER?", "Question one. Which square is lighter, left or right?",
      "They're the exact same gray. The background fools you.", d1),
    question(2, 4, "LEFT BARS OR RIGHT BARS?", "Question two. Which gray bars are lighter?",
      "Same gray again! The stripes around them change what you see.", d2),
    question(3, 4, "SAME COLOR THIS TIME?", "Question three. These two look about the same, right?",
      "Gotcha! This time they really are different. The right one is lighter.", d3),
    question(4, 4, "PURPLE OR ORANGE?", "Last one. The left red looks purple, the right looks orange.",
      "It's the same red! Only the stripes on top are different.", d4),
    Seg(["How many did you get right? Comment your score!"], d_outro,
        {"title": "HOW MANY DID YOU GET RIGHT?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
