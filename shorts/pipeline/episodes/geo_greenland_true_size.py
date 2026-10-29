"""Why Greenland looks as big as Africa (it isn't). Fri 30/10/2026, topic: countries & geography, format: why.

Areas: Greenland 2,166,086 km² (836,330 sq mi); Africa ~30.37 million km² (11.7 million sq mi) -> ~14x.
Mercator stretches lengths by 1/cos(latitude): at 60° everything is drawn twice as wide and twice as tall.
The slide is a true rotation on the sphere (geo.move), so the shrinking is the real Mercator effect.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import geo  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, pill, ramp, render  # noqa: E402

LAND = geo.land()
AFRICA = geo.continent("Africa")
GREEN = geo.country("Greenland", keep=0.01)
SRC, DST = (-41.0, 72.0), (21.0, 6.0)
WORLD = geo.world()
x0, _ = geo.mercator(-75, 0)
x1, _ = geo.mercator(70, 0)
_, y0 = geo.mercator(0, -38)
_, y1 = geo.mercator(0, 84)
CLOSE = geo.View(geo.mercator, x0, y0, x1, y1)
ORANGE = (1.0, 0.62, 0.25)


def base(ctx, view, slide=0.0, africa=1.0, green=1.0):
    ctx.rectangle(geo.X0, geo.Y0, geo.X1 - geo.X0, geo.Y1 - geo.Y0)
    ctx.clip()
    geo.ocean(ctx)
    geo.shape(ctx, LAND, view, geo.LAND)
    geo.shape(ctx, AFRICA, view, ORANGE, africa)
    geo.shape(ctx, geo.move(GREEN, SRC, DST, slide), view, BLUE, green, stroke=WHITE, width=2)
    ctx.reset_clip()


def label(ctx, s, sub, x, y, color, a):
    pill(ctx, s, x, y, color, a, size=40)
    if sub:
        pill(ctx, sub, x, y + 70, WHITE, a, size=30)


def d_intro(ctx, t, s):
    base(ctx, WORLD, africa=ramp(t, 1.2, 0.4), green=ramp(t, 0.4, 0.4))
    label(ctx, "GREENLAND", None, 300, 600, BLUE, ramp(t, 0.4, 0.4))
    label(ctx, "AFRICA", None, 760, 1080, ORANGE, ramp(t, 1.2, 0.4))


def d_sizes(ctx, t, s):
    base(ctx, CLOSE)
    a = ramp(t, s.mark(0) + 1.0, 0.4)
    label(ctx, "836,000 sq mi", "GREENLAND", 330, 820, BLUE, a)
    label(ctx, "11.7 MILLION sq mi", "AFRICA", 640, 1260, ORANGE, a)
    pill(ctx, "14x BIGGER", geo.CX, geo.Y0 + 70, YELLOW, ramp(t, s.mark(0) + 1.6, 0.3), size=56)


def d_why(ctx, t, s):
    base(ctx, CLOSE, africa=0.35, green=0.35)
    # same-size circles (400 km radius) at different latitudes: Mercator inflates them by 1/cos(lat)
    for i, lat in enumerate((0, 30, 50, 65, 75)):
        a = ramp(t, s.mark(1) + i * 0.35, 0.3)
        if a <= 0:
            continue
        x, y = CLOSE(-10, lat)
        r = 400 / 6371 * CLOSE.k / math.cos(math.radians(lat))
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1, 1)
        ctx.arc(0, 0, r * a, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(*YELLOW, 0.75)
        ctx.fill()
    pill(ctx, "MERCATOR MAP", geo.CX, geo.Y0 + 70, WHITE, 1.0, size=44)
    pill(ctx, "EVERY CIRCLE IS THE SAME SIZE", geo.CX, geo.Y1 - 70, YELLOW, ramp(t, s.mark(2), 0.3), size=38)


def d_slide(ctx, t, s):
    k = ramp(t, s.mark(0) + 0.6, 4.2)
    base(ctx, CLOSE, slide=k)
    a = ramp(t, s.mark(1), 0.4)
    pill(ctx, "TRUE SIZE", geo.CX, geo.Y1 - 70, BLUE, a, size=52)


def d_fit(ctx, t, s):
    base(ctx, CLOSE, slide=1.0)
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    x, y = CLOSE(*DST)
    ctx.arc(x, y, 150 + 12 * pulse, 0, 2 * math.pi)
    ctx.set_source_rgba(*WHITE, 0.6)
    ctx.set_line_width(5)
    ctx.stroke()
    pill(ctx, "AFRICA = 14 GREENLANDS", geo.CX, geo.Y1 - 70, YELLOW, ramp(t, 0.4, 0.3), size=46)


def d_outro(ctx, t, s):
    k = 1 - ramp(t, 0.2, 2.5)  # Greenland slides back home, so the end loops into the start
    base(ctx, CLOSE, slide=k)


SEGMENTS = [
    Seg(["On a world map, Greenland looks about as big as Africa."], d_intro,
        {"title": "GREENLAND IS LYING TO YOU"}, tail=0.3),
    Seg(["In reality, Africa is fourteen times bigger."], d_sizes,
        {"big": "14x", "sub": "THE REAL DIFFERENCE", "color": ORANGE}, sfx=[(0, 1.6, "ding")]),
    Seg(["The problem is the map.", "The Mercator projection stretches everything near the poles.",
         "These circles are all the same size in real life."], d_why,
        {"big": "WHY?", "sub": "THE MAP STRETCHES", "color": YELLOW}),
    Seg(["Now let's slide Greenland down to the equator.", "Watch it shrink to its true size."], d_slide,
        {"big": "WATCH", "sub": "SAME ISLAND, TRUE SIZE"}, tail=1.0, sfx=[(1, 0.3, "whoosh")]),
    Seg(["That's how small it really is. Africa could hold fourteen of them."], d_fit,
        {"big": "TINY", "sub": "THE REAL GREENLAND", "color": PINK}, sfx=[(0, 0.4, "ding")]),
    Seg(["Did this surprise you? Tell me in the comments!"], d_outro,
        {"title": "DID THIS SURPRISE YOU?"}, tail=0.8),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
