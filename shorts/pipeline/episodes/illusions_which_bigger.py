"""Which one is bigger? 4-round size/alignment quiz. Tue 03/11/2026, topic: optical illusions, format: interactive.

Facts (all four are classic, well-documented illusions; the drawings are built so the answers are exact):
- Jastrow (Joseph Jastrow, 1889): two identical ring sectors; the lower one looks bigger because its short inner
  edge sits next to the other's long outer edge. Drawn here with the same radii and angles.
- Ponzo (Mario Ponzo, 1911): two equal bars on converging lines; the one nearer the "horizon" looks longer because
  the brain reads it as farther away. Both bars are 230 px.
- Shepard tables (Roger Shepard, 1990, "Mind Sights"): the two table tops are the same parallelogram, one turned
  78 degrees; the legs make one read as long and thin, the other as short and wide.
- Poggendorff (J. C. Poggendorff, 1860): a diagonal hidden behind a bar seems to come out higher than it really does,
  so most people pick a line above the true continuation (here C; A and B are 115 and 45 px too high).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import illusions as il  # noqa: E402
from core import GREEN, PINK, Seg, ramp, render  # noqa: E402
from personagem import seg_pergunta  # noqa: E402
from quiz import answer, countdown, question  # noqa: E402

N = 4
CANTO = (il.X1 - 105, il.Y0 + 105)  # 3-2-1 timer in the panel corner, away from the drawings


def timer(ctx, t, s):
    countdown(ctx, t, s.mark(1), cx=CANTO[0], cy=CANTO[1])


def d_intro(ctx, t, s):
    ctx.save()
    il.jastrow(ctx, t * 1.6, sway=1.6)
    ctx.restore()


def d1(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.jastrow(ctx, t, overlay=ramp(t, r, 0.9))
    ctx.restore()
    timer(ctx, t, s)
    answer(ctx, t, r, "SAME SIZE", GREEN)


def d2(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.ponzo(ctx, t, fade=ramp(t, r, 0.6), slide=ramp(t, r + 0.4, 0.8))
    ctx.restore()
    timer(ctx, t, s)
    answer(ctx, t, r, "SAME LENGTH", GREEN)


def d3(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.shepard(ctx, match=ramp(t, r, 1.3))
    ctx.restore()
    timer(ctx, t, s)
    answer(ctx, t, r + 0.6, "SAME SHAPE", GREEN)


def d4(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.poggendorff(ctx, truth=ramp(t, r, 0.9))
    ctx.restore()
    timer(ctx, t, s)
    answer(ctx, t, r, "IT'S C!", PINK)


SEGMENTS = [
    Seg(["Four tests your brain will fail. Keep score!"], d_intro, {"title": "WHICH ONE IS BIGGER?"}, tail=0.15),
    question(1, N, "TOP OR BOTTOM?", "One. Which shape is bigger, top or bottom?",
             "Same size! Stack them and they match.", d1),
    question(2, N, "WHICH BAR IS LONGER?", "Two. Which yellow bar is longer?",
             "Exactly the same. The rails trick your brain.", d2),
    question(3, N, "LONG TABLE OR WIDE TABLE?", "Three. Which table top is bigger?",
             "Same table top, just turned!", d3),
    question(4, N, "WHICH LINE CONTINUES?", "Last one. Most people miss this. A, B or C?",
             "It's C! Most people pick A or B.", d4),
]
SEGMENTS.append(seg_pergunta("Which one fooled you? Be honest.", "WHICH ONE FOOLED YOU?",
                             fundo=lambda ctx, t, s: il.poggendorff(ctx, truth=1.0)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
