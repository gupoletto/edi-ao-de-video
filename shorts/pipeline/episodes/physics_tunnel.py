"""How long would it take to fall through the Earth? Thu 29/10/2026, topic: physics simulations, format: why/how.

Uniform-density Earth, no air or heat: simple harmonic motion, crossing time π·sqrt(R³/GM) ≈ 42.2 min,
top speed sqrt(GM/R) ≈ 7.9 km/s (~17,700 mph). With Earth's real dense core it is closer to 38 min
(Klotz 2015, Am. J. Phys.).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import physics as ph  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

SIM = ph.tunnel_sim(90)


def readout(ctx, x, v, sim_t):
    text_center(ctx, f"{int(sim_t // 60):02d}:{int(sim_t % 60):02d}", ph.CX, ph.Y0 + 90, 64, WHITE, "ExtraBold")
    mph = abs(v) * 2.23694
    text_center(ctx, f"{mph:,.0f} MPH", ph.CX, ph.Y1 - 70, 56, YELLOW, "ExtraBold")


def d_hook(ctx, t, s):
    ph.tunnel(ctx, 0, SIM)
    text_center(ctx, "?", ph.CX + 90, ph.CY - 340, 90, WHITE, "ExtraBold")


HALF = 2530  # seconds to cross (42.2 min); the centre is at HALF / 2


def run(ctx, t0, t1, a, b, t):
    """Animate simulated time from a to b while the clip's time t goes from t0 to t1."""
    k = min(1.0, max(0.0, (t - t0) / max(0.1, t1 - t0)))
    sim_t = a + (b - a) * k
    x, v = ph.tunnel(ctx, sim_t, SIM)
    readout(ctx, x, v, sim_t)


def d_fall(ctx, t, s):  # surface -> centre
    run(ctx, s.mark(1), s.dur - 0.1, 0, HALF / 2, t)


def d_center(ctx, t, s):  # hold at the centre, then centre -> far side
    run(ctx, s.mark(1), s.dur - 0.2, HALF / 2, HALF, t)


def d_back(ctx, t, s):  # hold at the far side, then fall back home
    run(ctx, s.mark(2), s.dur - 0.1, HALF, 2 * HALF, t)


SEGMENTS = [
    Seg(["Imagine a tunnel straight through the Earth. You jump in. How long until you pop out the other side?"],
        d_hook, {"title": "FALLING THROUGH THE EARTH"}, tail=0.3),
    Seg(["Let's simulate it, with no air and no heat.", 0.2,
         "Gravity pulls you toward the center, faster and faster."],
        d_fall, {"big": "THE FALL", "big_size": 96, "sub": "REAL GRAVITY SIMULATION", "color": BLUE}, tail=0.2),
    Seg(["At the center, you fly through at almost eighteen thousand miles per hour.",
         "Then gravity flips, and slows you down on the way up."],
        d_center, {"big": "THE CENTER", "big_size": 96, "sub": "TOP SPEED", "color": PINK}),
    Seg(["You reach the other side in about forty-two minutes, and stop right at the surface.",
         "With Earth's heavy core, it's closer to thirty-eight minutes.",
         "Don't grab the edge, and you fall back, forever."],
        d_back, {"big": "42 MINUTES", "big_size": 96, "sub": "TO THE OTHER SIDE", "color": BLUE}, sfx=[(0, 0.2, "ding")]),
    Seg(["Would you jump in? Tell me below."], d_hook, {"title": "WOULD YOU JUMP IN?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
