"""Guess the country from its shape, 5 questions. Fri 30/10/2026, topic: countries & geography, format: interactive.

Outlines: Natural Earth 1:50m (tiny far-off islands dropped, e.g. Easter Island). Facts: Chile is ~4,300 km
(2,700 mi) long and on average ~175 km wide; Madagascar is the 4th largest island; Mongolia is the most sparsely
populated sovereign country; Iceland sits on the Mid-Atlantic Ridge.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import geo  # noqa: E402
from core import BLUE, GREEN, WHITE, YELLOW, Seg, pill, ramp, render  # noqa: E402
from quiz import countdown, question  # noqa: E402

N = 5
SIL = (geo.X0, geo.Y0, geo.X1, geo.Y0 + 600)  # silhouette box
OPT_Y = (geo.Y0 + 680, geo.Y0 + 770, geo.Y0 + 860)
INSET = (geo.X1 - 300, geo.Y0 + 10, geo.X1 - 10, geo.Y0 + 175)
WORLD = geo.world(box=INSET, lat_top=78, lat_bottom=-56)
LAND = geo.land()
SHAPES = {n: geo.country(n, keep=0.03) for n in ("Italy", "Iceland", "Madagascar", "Chile", "Mongolia")}


def guess(name, options):
    rings = SHAPES[name]
    view = geo.fit(rings, box=SIL, pad=50)

    def draw(ctx, t, s):
        r = s.mark(2)
        k = ramp(t, r, 0.4)
        geo.shape(ctx, rings, view, tuple(WHITE[i] * (1 - k) + BLUE[i] * k for i in range(3)),
                  ramp(t, 0, 0.4), stroke=WHITE if k else None, width=3)
        for i, (y, opt) in enumerate(zip(OPT_Y, options)):
            right = opt == name
            if t < r:
                pill(ctx, f"{'ABC'[i]}.  {opt.upper()}", geo.CX, y, WHITE, ramp(t, 0.3 + 0.15 * i, 0.3), size=40)
            else:
                color = GREEN if right else (0.35, 0.37, 0.42)
                pill(ctx, f"{'ABC'[i]}.  {opt.upper()}", geo.CX, y, color, 1.0, size=40)
        countdown(ctx, t, s.mark(1), cx=INSET[2] - 90, cy=INSET[1] + 90)
        a = ramp(t, r + 0.5, 0.4)
        if a > 0:  # where it is on the world map
            ctx.rectangle(INSET[0], INSET[1], INSET[2] - INSET[0], INSET[3] - INSET[1])
            ctx.set_source_rgba(*geo.OCEAN, a)
            ctx.fill()
            ctx.save()
            ctx.rectangle(INSET[0], INSET[1], INSET[2] - INSET[0], INSET[3] - INSET[1])
            ctx.clip()
            geo.shape(ctx, LAND, WORLD, geo.LAND, a)
            geo.shape(ctx, rings, WORLD, YELLOW, a, stroke=YELLOW, width=2)
            ctx.restore()
    return draw


def d_intro(ctx, t, s):
    for i, n in enumerate(SHAPES):
        x = geo.X0 + 110 + i * 185
        y = geo.CY - 60 + (70 if i % 2 else -70)
        v = geo.fit(SHAPES[n], box=(x - 90, y - 120, x + 90, y + 120), pad=4)
        geo.shape(ctx, SHAPES[n], v, WHITE, ramp(t, 0.15 * i, 0.4))
    pill(ctx, "?", geo.CX, geo.Y1 - 140, YELLOW, ramp(t, 1.0, 0.3), size=72)


def d_outro(ctx, t, s):
    d_intro(ctx, t + 2, s)


SEGMENTS = [
    Seg(["Guess the country from its shape. Five questions, and the last one is hard."],
        d_intro, {"title": "GUESS THE COUNTRY FROM ITS SHAPE"}, tail=0.3),
    question(1, N, "THE EASY ONE", "Question one. This one is famous.",
             "Italy! The boot, kicking the island of Sicily.",
             guess("Italy", ["Greece", "Italy", "Spain"])),
    question(2, N, "AN ISLAND UP NORTH", "Question two. An island in the North Atlantic.",
             "Iceland! It sits right on top of two tectonic plates.",
             guess("Iceland", ["Ireland", "Cuba", "Iceland"])),
    question(3, N, "A BIG ISLAND", "Question three. Another island, but much warmer.",
             "Madagascar, the fourth largest island in the world.",
             guess("Madagascar", ["Madagascar", "Sri Lanka", "Cuba"])),
    question(4, N, "THE LONGEST ONE", "Question four. Long and skinny.",
             "Chile! About twenty seven hundred miles long, but very narrow.",
             guess("Chile", ["Peru", "Norway", "Chile"])),
    question(5, N, "THE HARD ONE", "Last one. This one is landlocked in Asia.",
             "Mongolia, the most sparsely populated country on Earth.",
             guess("Mongolia", ["Kazakhstan", "Mongolia", "Turkmenistan"])),
    Seg(["How many did you get? Comment your score!"], d_outro, {"title": "HOW MANY DID YOU GET?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
