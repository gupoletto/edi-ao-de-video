"""Can you predict the winner? 4 physics races. Thu 29/10/2026, topic: physics simulations, format: interactive.

No air resistance in any race. Q1/Q2: fall time sqrt(2h/g) does not depend on mass or sideways speed.
Q3: the cycloid is the brachistochrone (fastest frictionless path). Q4: period ∝ sqrt(L), so the 1/4-length
pendulum swings back in half the time.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import physics as ph  # noqa: E402
from core import GREEN, WHITE, Seg, render, text_center  # noqa: E402
from quiz import answer, countdown, question  # noqa: E402


def labels(ctx, a, b, xa=330, xb=750, y=ph.Y1 - 60):
    text_center(ctx, a, xa, y, 38, WHITE)
    text_center(ctx, b, xb, y, 38, WHITE)


def q1(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    ph.drop_pair(ctx, t - r)
    ctx.restore()
    labels(ctx, "HEAVY", "LIGHT")
    countdown(ctx, t, s.mark(1), cy=ph.Y1 - 170)
    answer(ctx, t, r + 0.6, "A TIE!", GREEN, cy=ph.Y1 - 170)


def q2(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    ph.drop_pair(ctx, t - r, thrown=True)
    ctx.restore()
    labels(ctx, "DROPPED", "THROWN", xa=250, xb=650)
    countdown(ctx, t, s.mark(1), cy=ph.Y1 - 170)
    answer(ctx, t, r + 0.6, "A TIE AGAIN!", GREEN, cy=ph.Y1 - 170)


def q3(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    ph.cycloid_race(ctx, t - r)
    ctx.restore()
    labels(ctx, "STRAIGHT", "CURVED", xa=300, xb=700, y=ph.Y1 - 60)
    countdown(ctx, t, s.mark(1), cy=ph.Y1 - 170)
    answer(ctx, t, r + 0.9, "CURVED WINS", GREEN, cy=ph.Y1 - 170)


def q4(ctx, t, s):
    r = s.mark(2)
    ctx.save()
    ph.pendulum_race(ctx, t - r)
    ctx.restore()
    labels(ctx, "LONG", "SHORT", xa=350, xb=730)
    countdown(ctx, t, s.mark(1), cy=ph.Y1 - 170)
    answer(ctx, t, r + 1.0, "SHORT WINS", GREEN, cy=ph.Y1 - 170)


def d_intro(ctx, t, s):
    ph.cycloid_race(ctx, (t % 2.2) - 0.3)


SEGMENTS = [
    Seg(["Can you predict the winner? Four physics races. Keep score!"], d_intro,
        {"title": "CAN YOU PREDICT THE WINNER?"}, tail=0.3),
    question(1, 4, "HEAVY OR LIGHT?", "Race one. A heavy ball and a light ball fall with no air. Which lands first?",
             "It's a tie! Without air, gravity pulls everything down at the same rate.", q1),
    question(2, 4, "DROPPED OR THROWN?", "Race two. One ball is dropped, one is thrown sideways. Which lands first?",
             "Another tie! Moving sideways doesn't change how fast you fall.", q2),
    question(3, 4, "STRAIGHT OR CURVED?", "Race three. A straight ramp, or a curved one that dips lower?",
             "The curve wins, even though it's longer. It builds speed sooner.", q3),
    question(4, 4, "LONG OR SHORT?", "Last race. Which pendulum swings back to the start first?",
             "The short one, in exactly half the time. Length sets the beat.", q4),
    Seg(["How many did you get right? Comment your score!"], d_intro,
        {"title": "HOW MANY DID YOU GET RIGHT?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
