"""5 oddly satisfying loops, ranked (#5 -> #1). Sun 01/11/2026, topic: satisfying rankings (swap from mythology),
format: ranking. All motion drawn by code (shorts/pipeline/satisfying.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import satisfying as sa  # noqa: E402
from core import BLUE, PINK, Seg, render  # noqa: E402

DOTS = ["5", "4", "3", "2", "1"]


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def d_intro(ctx, t, s):
    sa.gears(ctx, t + 3)


def d_outro(ctx, t, s):
    sa.perfect_fit(ctx, t)


SEGMENTS = [
    Seg(["Five oddly satisfying loops. Rank them with me, and number one is the best."], d_intro,
        {"title": "5 ODDLY SATISFYING LOOPS"}, tail=0.3),
    Seg(["Number five. Three gears, and every tooth meets perfectly.", 1.0],
        lambda c, t, s: sa.gears(c, t), head(5, "PERFECT GEARS"), tail=0.4),
    Seg(["Number four. Thirty six dominoes, one push.", 1.0],
        lambda c, t, s: sa.dominoes(c, t, start=0.6), head(4, "THE DOMINO SNAKE"), tail=0.4),
    Seg(["Number three. Sort every color into its own tube.", 2.2],
        lambda c, t, s: sa.ball_sort(c, t, passo=0.4), head(3, "BALL SORT"), tail=0.4),
    Seg(["Number two. Every shape finds its hole.", 1.2],
        lambda c, t, s: sa.perfect_fit(c, t), head(2, "PERFECT FIT"), tail=0.4),
    Seg(["And number one. The line clear. One block, and the whole row is gone.", 0.6],
        lambda c, t, s: sa.line_clear(c, t), head(1, "THE LINE CLEAR"), tail=0.6),
    Seg(["Which one was the most satisfying? Comment your number one."], d_outro,
        {"title": "WHICH ONE WAS YOUR #1?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
