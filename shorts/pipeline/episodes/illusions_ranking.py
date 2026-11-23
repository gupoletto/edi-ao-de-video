"""5 optical illusions ranked (#5 -> #1). Tuesday 27/10/2026, topic: optical illusions, format: ranking."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import illusions as il  # noqa: E402
from core import BLUE, GREEN, PINK, Seg, ramp, render, pill  # noqa: E402

DOTS = ["5", "4", "3", "2", "1"]


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def verdict(ctx, text, a):
    pill(ctx, text, 540, 1300, GREEN, a)


def d_intro(ctx, t, s):
    il.stepping_feet(ctx, t + 2)


def d5(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.muller_lyer(ctx, fins=1 - 0.85 * ramp(t, r + 1.6, 0.8), guides=ramp(t, r, 0.8))
    ctx.restore()
    verdict(ctx, "SAME LENGTH", ramp(t, r + 0.6, 0.3))


def d4(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.ebbinghaus(ctx, reveal=ramp(t, r, 0.8), slide=ramp(t, r + 1.0, 0.9))
    ctx.restore()
    verdict(ctx, "SAME SIZE", ramp(t, r + 0.6, 0.3))


def d3(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.hering(ctx, reveal=ramp(t, r, 0.9), spin=0.04 * t)
    ctx.restore()
    verdict(ctx, "PERFECTLY STRAIGHT", ramp(t, r + 0.6, 0.3))


def d2(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.cafe_wall(ctx, shift=1 - ramp(t, r + 0.4, 1.4))
    ctx.restore()
    verdict(ctx, "ALL PARALLEL", ramp(t, r + 0.6, 0.3))


def d1(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    il.stepping_feet(ctx, t, stripes=1 - ramp(t, r, 0.9))
    ctx.restore()
    verdict(ctx, "SAME STEADY SPEED", ramp(t, r + 0.6, 0.3))


def d_outro(ctx, t, s):
    ctx.save()
    il.muller_lyer(ctx)
    ctx.restore()


SEGMENTS = [
    Seg(["These five optical illusions will break your brain."], d_intro,
        {"title": "5 ILLUSIONS THAT BREAK YOUR BRAIN"}, tail=0.3),
    Seg(["Number five. Which line is longer? The top one, right?", 0.7,
         "Nope. They're exactly the same length. The fins trick you."], d5,
        head(5, "MÜLLER-LYER LINES"), sfx=[(2, 0.6, "ding")]),
    Seg(["Number four. Which orange circle is bigger?", 0.8,
         "Same size! Big neighbors make a circle look small."], d4,
        head(4, "EBBINGHAUS CIRCLES"), sfx=[(2, 0.6, "ding")]),
    Seg(["Number three. These red lines bend outward, don't they?", 0.7,
         "Remove the rays. They were perfectly straight all along."], d3,
        head(3, "HERING ILLUSION"), sfx=[(2, 0.6, "ding")]),
    Seg(["Number two. Those gray lines look tilted.", 0.8,
         "Line up the tiles, and they're all perfectly parallel."], d2,
        head(2, "CAFÉ WALL"), sfx=[(2, 0.6, "ding")]),
    Seg(["And number one. Watch these blocks walk, step by step.", 1.6,
         "Now remove the stripes. They glide at the same steady speed."], d1,
        head(1, "STEPPING FEET"), sfx=[(2, 0.6, "ding")], tail=1.0),
    Seg(["Which one fooled you the most? Tell me in the comments."], d_outro,
        {"title": "WHICH ONE FOOLED YOU THE MOST?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
