"""5 genius mechanisms, ranked (#5 -> #1). Thu 05/11/2026, topic: how it works, format: ranking (conflict at #2).

Facts:
- pin tumbler lock (Linus Yale Sr./Jr., 1840s-1860s): the key's cuts lift each pin pair so the gap between the lower
  and upper pin sits exactly on the shear line; then the plug can turn;
- ratchet + pawl: turns one way, locks the other (bicycle freewheel, socket wrench);
- Geneva drive: a continuously turning pin wheel moves a 4-slot wheel a quarter turn, then locks it; used for the
  intermittent film advance of movie projectors;
- anchor escapement (around 1657-1670, Robert Hooke / William Clement): lets the escape wheel advance one tooth per
  pendulum swing, which is what makes pendulum clocks tick; used for over 300 years;
- planetary gears: sun 12 teeth, 3 planets of 12, ring 36 (36 = 12 + 2 * 12). Ring held: output = input * 12 / 48
  = 1/4, a 4:1 reduction in one small circle (automatic gearboxes, electric screwdrivers, wind turbines).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mecanismos as mc  # noqa: E402
import personagem as pq  # noqa: E402
from core import BLUE, PINK, Seg, render  # noqa: E402

DOTS = ["5", "4", "3", "2", "1"]


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


SEGMENTS = [
    Seg(["Five genius mechanisms, ranked."], lambda c, t, s: mc.planetaria(c, t + 2, w=2.4, marca=False),
        {"title": "5 GENIUS MECHANISMS, RANKED"}, tail=0.1),
    Seg(["Number five. The pin lock. The right key lifts every pin to one line.", 0.4],
        lambda c, t, s: mc.fechadura(c, t, entra=(0.2, 2.9)), head(5, "THE PIN LOCK"), tail=0.2),
    Seg(["Number four. The ratchet. It spins one way, and locks the other."],
        lambda c, t, s: mc.catraca(c, t, frente=(0.0, 2.0), volta=(2.0, 4.0)), head(4, "THE RATCHET"), tail=0.5),
    Seg(["Number three. The Geneva drive. Smooth spinning in, perfect steps out."],
        lambda c, t, s: mc.geneva(c, t, w=2.2), head(3, "THE GENEVA DRIVE"), tail=0.3),
    Seg(["Number two. The clock escapement. One tooth per swing, for over three hundred years.",
         "Looks like the winner. But."],
        lambda c, t, s: mc.escapamento(c, t), head(2, "THE ESCAPEMENT"), tail=0.2,
        sfx=[(0, 0.7, "tick"), (0, 1.4, "tick"), (0, 2.1, "tick"), (0, 2.8, "tick")]),
    Seg(["Number one. Planetary gears. Four times slower, inside one tiny circle.",
         "They're in car gearboxes and power drills."],
        lambda c, t, s: mc.planetaria(c, t), head(1, "PLANETARY GEARS"), tail=0.4),
]
SEGMENTS.append(pq.seg_pergunta("Which one deserves number one?", "WHICH ONE IS YOUR #1?",
                                fundo=lambda c, t, s: mc.planetaria(c, t + 8, marca=False)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
