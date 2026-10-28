"""Which is bigger? Space edition, 4 questions. Wed 28/10/2026, topic: space, format: interactive.

Mean diameters (NASA): Earth 12,742 km, Venus 12,104; Moon 3,474, Pluto 2,377; Ganymede 5,268, Mercury 4,879;
Uranus 51,118, Neptune 49,528.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import space as sp  # noqa: E402
from core import GREEN, WHITE, Seg, ramp, render, text_center  # noqa: E402
from quiz import answer, countdown, question  # noqa: E402

CX, CY = sp.CX, sp.CY


def pair(a, da, b, db, winner):
    """Two bodies shown the same size, then resized to true scale at the reveal."""
    def draw(ctx, t, s):
        sp.sky(ctx, t)
        r = s.mark(2)
        k = ramp(t, r, 1.0)
        big = max(da, db)
        for x, name, d in ((300, a, da), (780, b, db)):
            rad = 170 * (1 - k) + 200 * (d / big) * k
            sp.planet(ctx, name, x, CY - 60, rad, spin=t * 0.05)
            text_center(ctx, name.upper(), x, CY + 200, 40, WHITE)
            text_center(ctx, f"{d:,} km", x, CY + 250, 32, (0.7, 0.75, 0.85), alpha=ramp(t, r + 0.6, 0.4))
        countdown(ctx, t, s.mark(1))
        answer(ctx, t, r, f"{winner.upper()} IS BIGGER", GREEN)
    return draw


def d_intro(ctx, t, s):
    sp.sky(ctx, t)
    sp.planet(ctx, "uranus", 330, CY - 40, 170)
    sp.planet(ctx, "neptune", 750, CY - 40, 170)
    text_center(ctx, "?", CX, CY, 150, WHITE, "ExtraBold")


SEGMENTS = [
    Seg(["Which is bigger? Four space questions. Watch out for number three!"], d_intro,
        {"title": "WHICH IS BIGGER? SPACE EDITION"}, tail=0.3),
    question(1, 4, "EARTH OR VENUS?", "Question one. Earth or Venus?",
             "Earth wins, but only by about five percent. Venus is almost our twin.",
             pair("earth", 12742, "venus", 12104, "earth")),
    question(2, 4, "MOON OR PLUTO?", "Question two. Our Moon or Pluto?",
             "Our Moon! Pluto is only about two thirds as wide.",
             pair("moon", 3474, "pluto", 2377, "moon")),
    question(3, 4, "MERCURY OR GANYMEDE?", "Question three. The planet Mercury, or Jupiter's moon Ganymede?",
             "Ganymede! A moon that's bigger than a planet.",
             pair("mercury", 4879, "ganymede", 5268, "ganymede")),
    question(4, 4, "URANUS OR NEPTUNE?", "Last one. Uranus or Neptune?",
             "Uranus is slightly wider, even though Neptune is heavier.",
             pair("uranus", 51118, "neptune", 49528, "uranus")),
    Seg(["How many did you get right? Comment your score!"], d_intro,
        {"title": "HOW MANY DID YOU GET RIGHT?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
