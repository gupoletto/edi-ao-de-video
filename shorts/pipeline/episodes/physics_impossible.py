"""5 physics simulations that look impossible (#5 -> #1). Thu 29/10/2026, topic: physics simulations, format: ranking.

All motion is integrated numerically in physics.py. Checked: blocks with mass ratio 1 / 100 / 10,000 collide
3 / 31 / 314 times (Galperin 2003); figure-eight orbit from Chenciner & Montgomery (2000).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import physics as ph  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

DOTS = ["5", "4", "3", "2", "1"]
HEX = ph.hexagon_sim(16)
ROPE = ph.rope_sim(14)
FIG8 = ph.three_body_sim(16)
FIG8_NUDGED = ph.three_body_sim(16, nudge=0.02)
PI = ph.pi_blocks_sim(10000)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def d_intro(ctx, t, s):
    ph.hexagon(ctx, t + 4, HEX)


def d5(ctx, t, s):
    ph.newtons_cradle(ctx, t)


def d4(ctx, t, s):
    ph.hexagon(ctx, t, HEX)


def d3(ctx, t, s):
    ph.rope(ctx, t, ROPE)


def d2(ctx, t, s):
    nudged = t >= s.mark(2)
    if nudged:  # restart from the same start, 4x speed so the chaos shows within the clip
        ph.three_body(ctx, (t - s.mark(2)) * 4, FIG8_NUDGED)
    else:
        ph.three_body(ctx, t, FIG8)
    text_center(ctx, "NUDGED 2%" if nudged else "PERFECT FIGURE 8", ph.CX, ph.Y1 - 60, 44,
                PINK if nudged else YELLOW, "ExtraBold")


def d1(ctx, t, s):
    start = s.mark(1)
    # play the whole event-driven run (last collision at t = PI[-1][0]) before the segment ends
    tt = max(0.0, t - start) * (PI[-1][0] + 0.3) / max(1.0, s.dur - start - 1.2)
    ctx.save()
    n = ph.pi_blocks(ctx, tt, PI)
    ctx.restore()
    text_center(ctx, "10,000 : 1", ph.CX, ph.Y0 + 90, 48, WHITE, "ExtraBold")
    text_center(ctx, f"COLLISIONS: {n}", ph.CX, ph.Y1 - 80, 64, YELLOW if n < 314 else PINK, "ExtraBold")


def d_outro(ctx, t, s):
    ph.newtons_cradle(ctx, t)


SEGMENTS = [
    Seg(["These five physics simulations look impossible, but every one is real math."], d_intro,
        {"title": "5 PHYSICS SIMULATIONS THAT LOOK IMPOSSIBLE"}, tail=0.3),
    Seg(["Number five. Newton's cradle.", "The energy passes straight through the middle balls, so only the last one swings out."],
        d5, head(5, "NEWTON'S CRADLE")),
    Seg(["Number four. A ball inside a spinning hexagon.", "Gravity pulls it down, and the moving walls keep kicking it back up."],
        d4, head(4, "SPINNING HEXAGON")),
    Seg(["Number three. A rope made of forty linked points.", "Drop it, and the tip whips around faster than the rest."],
        d3, head(3, "FALLING ROPE")),
    Seg(["Number two. Three stars chasing each other in a perfect figure eight.", "It's a real solution to the three-body problem.",
         "But nudge one star by two percent, and the dance falls apart."],
        d2, head(2, "THREE-BODY PROBLEM"), sfx=[(2, 0, "whoosh")]),
    Seg(["And number one. A small block, a wall, and a block ten thousand times heavier.", 0.2,
         "Count every collision. Three hundred fourteen. The first digits of pi!"],
        d1, head(1, "BLOCKS THAT COUNT PI"), sfx=[(2, 2.4, "ding")], tail=0.8),
    Seg(["Which one blew your mind? Tell me in the comments."], d_outro,
        {"title": "WHICH ONE BLEW YOUR MIND?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
