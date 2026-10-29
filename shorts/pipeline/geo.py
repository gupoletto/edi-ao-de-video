"""Maps drawn from Natural Earth (public domain): country outlines, Mercator, true-size moves on the sphere."""
import json
import math
import os
import urllib.request

from core import AREA, CACHE

NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/{}.geojson"
X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2
OCEAN = (0.07, 0.16, 0.27)
LAND = (0.20, 0.27, 0.33)
_files = {}


def _load(name):
    if name not in _files:
        p = os.path.join(CACHE, "naturalearth", name + ".geojson")
        if not os.path.exists(p):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            urllib.request.urlretrieve(NE_URL.format(name), p)
        with open(p, encoding="utf-8") as f:
            _files[name] = json.load(f)["features"]
    return _files[name]


def _polys(geom):
    return geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]


def ring_area(r):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(r, r[1:] + r[:1]))) / 2


def country(name, res="50m", keep=0.0):
    """Outer rings (lon, lat) of a country; keep drops islands smaller than keep x the largest one."""
    for f in _load(f"ne_{res}_admin_0_countries"):
        if f["properties"]["NAME"] == name:
            rings = [p[0] for p in _polys(f["geometry"])]
            big = max(ring_area(r) for r in rings)
            return [r for r in rings if ring_area(r) >= keep * big]
    raise KeyError(name)


def land():
    return [p[0] for f in _load("ne_50m_land") for p in _polys(f["geometry"])]


def continent(name):
    """All country rings of a continent (drawn without strokes, the borders disappear)."""
    return [p[0] for f in _load("ne_50m_admin_0_countries") if f["properties"]["CONTINENT"] == name
            for p in _polys(f["geometry"])]


# ---------- projections ----------

def mercator(lon, lat):
    lat = max(-84.0, min(84.0, lat))
    return math.radians(lon), math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def _vec(lon, lat):
    lo, la = math.radians(lon), math.radians(lat)
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))


def _lonlat(v):
    return math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(max(-1, min(1, v[2]))))


def move(rings, src, dst, k=1.0):
    """Rotate the shape on the globe so point src (lon, lat) goes a fraction k of the way to dst.
    Rotation keeps the true size: drawn in Mercator, the shape shrinks or grows as it changes latitude."""
    a, b = _vec(*src), _vec(*dst)
    axis = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    n = math.sqrt(sum(c * c for c in axis))
    if n < 1e-9 or k == 0:
        return rings
    ux, uy, uz = (c / n for c in axis)
    ang = math.atan2(n, sum(x * y for x, y in zip(a, b))) * k
    c, s = math.cos(ang), math.sin(ang)

    def rot(v):
        x, y, z = v
        d = ux * x + uy * y + uz * z
        return (x * c + (uy * z - uz * y) * s + ux * d * (1 - c),
                y * c + (uz * x - ux * z) * s + uy * d * (1 - c),
                z * c + (ux * y - uy * x) * s + uz * d * (1 - c))
    return [[_lonlat(rot(_vec(*p))) for p in r] for r in rings]


class View:
    """Maps projected coordinates to screen pixels."""

    def __init__(self, proj, x0, y0, x1, y1, box=(X0, Y0, X1, Y1), pad=40):
        self.proj = proj
        bw, bh = box[2] - box[0] - 2 * pad, box[3] - box[1] - 2 * pad
        self.k = min(bw / (x1 - x0), bh / (y1 - y0))
        self.ox = (box[0] + box[2]) / 2 - self.k * (x0 + x1) / 2
        self.oy = (box[1] + box[3]) / 2 + self.k * (y0 + y1) / 2

    def __call__(self, lon, lat):
        x, y = self.proj(lon, lat)
        return self.ox + self.k * x, self.oy - self.k * y


def fit(rings, proj=None, box=(X0, Y0, X1, Y1), pad=40):
    """View that frames these rings; default projection is local equirectangular (shape-true at its latitude)."""
    if proj is None:
        lat0 = sum(p[1] for r in rings for p in r) / sum(len(r) for r in rings)
        cl = math.cos(math.radians(lat0))
        proj = lambda lon, lat: (math.radians(lon) * cl, math.radians(lat))  # noqa: E731
    pts = [proj(*p) for r in rings for p in r]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return View(proj, min(xs), min(ys), max(xs), max(ys), box, pad)


def world(box=(X0, Y0, X1, Y1), lat_top=80, lat_bottom=-60, pad=0):
    x0, y0 = mercator(-180, lat_bottom)
    x1, y1 = mercator(180, lat_top)
    return View(mercator, x0, y0, x1, y1, box, pad)


def path(ctx, rings, view):
    for r in rings:
        for i, p in enumerate(r):
            x, y = view(*p)
            (ctx.line_to if i else ctx.move_to)(x, y)
        ctx.close_path()


def shape(ctx, rings, view, fill, alpha=1.0, stroke=None, width=3):
    path(ctx, rings, view)
    ctx.set_source_rgba(*fill, alpha)
    if stroke:
        ctx.fill_preserve()
        ctx.set_line_join(1)  # round
        ctx.set_line_width(width)
        ctx.set_source_rgba(*stroke, alpha)
        ctx.stroke()
    else:
        ctx.fill()


def ocean(ctx, box=(X0, Y0, X1, Y1)):
    ctx.rectangle(box[0], box[1], box[2] - box[0], box[3] - box[1])
    ctx.set_source_rgb(*OCEAN)
    ctx.fill()


def km_per_px(view):
    """Kilometres per screen pixel in a local equirectangular view (see fit)."""
    return 6371.0 / view.k


def scale_bar(ctx, view, km, label, x, y, color=(1, 1, 1)):
    from core import text_center
    w = km / km_per_px(view)
    ctx.set_source_rgb(*color)
    ctx.rectangle(x, y, w, 8)
    ctx.fill()
    for xx in (x, x + w):
        ctx.rectangle(xx - 2, y - 10, 4, 28)
        ctx.fill()
    text_center(ctx, label, x + w / 2, y + 52, 30, color, "SemiBold")
