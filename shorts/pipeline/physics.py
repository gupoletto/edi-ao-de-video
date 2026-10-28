"""Physics simulations, integrated numerically and drawn with cairo. Each sim precomputes its states once;
draw functions take the time t (seconds) and look the state up."""
import math

import cairo
import numpy as np

from core import AREA, round_rect

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2
FPS = 30


def panel(ctx, rgb=(0.05, 0.06, 0.10)):
    round_rect(ctx, X0, Y0, X1 - X0, Y1 - Y0, 36)
    ctx.set_source_rgb(*rgb)
    ctx.fill_preserve()
    ctx.clip()


def ball(ctx, x, y, r, rgb):
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r)
    g.add_color_stop_rgb(0, min(1, rgb[0] + 0.35), min(1, rgb[1] + 0.35), min(1, rgb[2] + 0.35))
    g.add_color_stop_rgb(1, rgb[0] * 0.7, rgb[1] * 0.7, rgb[2] * 0.7)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()


# ---------- Newton's cradle (ideal elastic: the swing passes straight through) ----------

def newtons_cradle(ctx, t):
    panel(ctx)
    n, r, L = 5, 52, 520
    top = Y0 + 110
    ctx.set_source_rgb(0.6, 0.62, 0.68)
    ctx.rectangle(CX - 330, top - 14, 660, 14)
    ctx.fill()
    w = 2 * math.pi / (2 * math.pi * math.sqrt(L / 9.81 / 300))  # visual period ~1.6 s
    s = 0.55 * math.sin(w * t)
    for i in range(n):
        px = CX + (i - 2) * 2 * r
        a = s if (i == 0 and s < 0) or (i == n - 1 and s > 0) else 0.0
        bx, by = px + L * math.sin(a), top + L * math.cos(a)
        ctx.set_source_rgba(1, 1, 1, 0.6)
        ctx.set_line_width(3)
        ctx.move_to(px, top)
        ctx.line_to(bx, by)
        ctx.stroke()
        ball(ctx, bx, by, r, (0.75, 0.78, 0.85))


# ---------- ball in a spinning hexagon ----------

def _hexagon(theta, R):
    return [(CX + R * math.cos(theta + k * math.pi / 3), CY + R * math.sin(theta + k * math.pi / 3)) for k in range(6)]


def hexagon_sim(dur, R=400, br=30, omega=0.9, g=1400.0, e=0.92):
    dt = 1 / (FPS * 8)
    p, v = np.array([CX, CY - 150.0]), np.array([260.0, 0.0])
    out = []
    for i in range(int(dur * FPS * 8)):
        th = omega * i * dt
        v[1] += g * dt
        p = p + v * dt
        pts = _hexagon(th, R)
        for k in range(6):
            a, b = np.array(pts[k]), np.array(pts[(k + 1) % 6])
            d = b - a
            nrm = np.array([-d[1], d[0]]) / np.linalg.norm(d)
            if np.dot(np.array([CX, CY]) - a, nrm) < 0:
                nrm = -nrm  # point inward
            dist = np.dot(p - a, nrm)
            if dist < br:
                wall_v = omega * np.array([-(p[1] - CY), p[0] - CX])  # velocity of the wall at the contact
                rel = v - wall_v
                vn = np.dot(rel, nrm)
                if vn < 0:
                    rel = rel - (1 + e) * vn * nrm
                    v = rel + wall_v
                p = p + (br - dist) * nrm
        if i % 8 == 0:
            out.append((p.copy(), th))
    return out


def hexagon(ctx, t, sim, trail=24):
    panel(ctx)
    i = min(len(sim) - 1, int(t * FPS))
    p, th = sim[i]
    pts = _hexagon(th, 400)
    ctx.set_line_width(10)
    ctx.set_source_rgb(0.36, 0.78, 0.98)
    ctx.move_to(*pts[0])
    for q in pts[1:]:
        ctx.line_to(*q)
    ctx.close_path()
    ctx.stroke()
    for j in range(max(0, i - trail), i):
        a = (j - i + trail) / trail
        ctx.set_source_rgba(1, 0.55, 0.15, 0.35 * a)
        ctx.arc(*sim[j][0], 30 * a, 0, 2 * math.pi)
        ctx.fill()
    ball(ctx, p[0], p[1], 30, (1.0, 0.5, 0.1))


# ---------- swinging rope (Verlet points + distance constraints) ----------

def rope_sim(dur, n=40, seg=17.0, g=1500.0):
    dt = 1 / (FPS * 4)
    anchor = np.array([CX, Y0 + 90])
    pos = np.array([anchor + [seg * i, 0.0] for i in range(n)])  # starts horizontal, falls and swings
    prev = pos.copy()
    out = []
    for i in range(int(dur * FPS * 4)):
        vel = (pos - prev) * 0.999
        prev = pos.copy()
        pos = pos + vel + np.array([0, g]) * dt * dt
        for _ in range(25):
            pos[0] = anchor
            d = pos[1:] - pos[:-1]
            L = np.linalg.norm(d, axis=1, keepdims=True)
            corr = d * (1 - seg / L) * 0.5
            pos[1:] -= corr
            pos[:-1] += corr
        pos[0] = anchor
        if i % 4 == 0:
            out.append(pos.copy())
    return out


def rope(ctx, t, sim):
    panel(ctx)
    pos = sim[min(len(sim) - 1, int(t * FPS))]
    ctx.set_line_width(9)
    ctx.set_line_cap(1)
    ctx.set_line_join(1)
    ctx.set_source_rgb(0.95, 0.80, 0.35)
    ctx.move_to(*pos[0])
    for q in pos[1:]:
        ctx.line_to(*q)
    ctx.stroke()
    ball(ctx, *pos[-1], 22, (1.0, 0.35, 0.45))
    ctx.set_source_rgb(0.7, 0.7, 0.75)
    ctx.arc(*pos[0], 12, 0, 2 * math.pi)
    ctx.fill()


# ---------- three-body figure-eight (Chenciner & Montgomery 2000), G = m = 1 ----------

def three_body_sim(dur, nudge=0.0, speed=1.6):
    r = np.array([[-0.97000436, 0.24308753], [0.97000436, -0.24308753], [0.0, 0.0]])
    v3 = np.array([-0.93240737, -0.86473146])
    v = np.array([-v3 / 2, -v3 / 2, v3])
    r[2] += [nudge, 0]
    sub = 40
    dt = speed / FPS / sub

    def acc(r):
        a = np.zeros_like(r)
        for i in range(3):
            for j in range(3):
                if i != j:
                    d = r[j] - r[i]
                    a[i] += d / (np.dot(d, d) + 1e-6) ** 1.5
        return a

    out, a = [], acc(r)
    for f in range(int(dur * FPS)):
        out.append(r.copy())
        for _ in range(sub):
            r = r + v * dt + 0.5 * a * dt * dt
            a2 = acc(r)
            v = v + 0.5 * (a + a2) * dt
            a = a2
    return out


def three_body(ctx, t, sim, trail=70, scale=380):
    panel(ctx, (0.02, 0.025, 0.06))
    i = min(len(sim) - 1, int(t * FPS))
    cols = [(1.0, 0.45, 0.35), (0.40, 0.75, 1.0), (1.0, 0.85, 0.30)]
    for k in range(3):
        ctx.set_line_width(4)
        for j in range(max(1, i - trail), i + 1):
            a = (j - i + trail) / trail
            p0, p1 = sim[j - 1][k], sim[j][k]
            ctx.set_source_rgba(*cols[k], 0.8 * a)
            ctx.move_to(CX + p0[0] * scale, CY - 40 - p0[1] * scale)
            ctx.line_to(CX + p1[0] * scale, CY - 40 - p1[1] * scale)
            ctx.stroke()
    for k in range(3):
        p = sim[i][k]
        ball(ctx, CX + p[0] * scale, CY - 40 - p[1] * scale, 26, cols[k])


# ---------- colliding blocks that count pi (Galperin 2003) ----------

def pi_blocks_sim(ratio, v_big=-1.0):
    """Event-driven elastic collisions: small block (mass 1) between a wall and a big block (mass ratio).
    Returns list of (time, x_small, v_small, x_big, v_big, count) at every event."""
    m, M = 1.0, float(ratio)
    xs, vs, xb, vb = 1.0, 0.0, 2.5, v_big
    t, n, ev = 0.0, 0, [(0.0, xs, vs, xb, vb, 0)]
    while True:
        cand = []
        if vb < vs:
            cand.append(((xb - xs) / (vs - vb), "blocks"))
        if vs < 0:
            cand.append((-xs / vs, "wall"))
        if not cand:
            break
        dtc, kind = min(cand)
        t += dtc
        xs, xb = xs + vs * dtc, xb + vb * dtc
        if kind == "blocks":
            vs, vb = ((m - M) * vs + 2 * M * vb) / (m + M), ((M - m) * vb + 2 * m * vs) / (m + M)
        else:
            vs = -vs
        n += 1
        ev.append((t, xs, vs, xb, vb, n))
    return ev


def pi_blocks_state(ev, t):
    lo = 0
    for k in range(len(ev)):
        if ev[k][0] <= t:
            lo = k
        else:
            break
    t0, xs, vs, xb, vb, n = ev[lo]
    d = t - t0
    return xs + vs * d, xb + vb * d, n


def pi_blocks(ctx, t, ev, time_scale=1.0):
    panel(ctx)
    xs, xb, n = pi_blocks_state(ev, t * time_scale)
    floor = CY + 160
    wall = X0 + 70
    ppu = 150
    ctx.set_source_rgb(0.6, 0.62, 0.68)
    ctx.rectangle(X0, floor, X1 - X0, 6)
    ctx.fill()
    ctx.rectangle(wall - 16, floor - 520, 16, 520)
    ctx.fill()
    s_small, s_big = 60, 200
    ctx.set_source_rgb(0.36, 0.78, 0.98)
    ctx.rectangle(wall + xs * ppu - s_small, floor - s_small, s_small, s_small)
    ctx.fill()
    bx = wall + xb * ppu
    if bx < X1 + 50:
        ctx.set_source_rgb(1.0, 0.36, 0.54)
        ctx.rectangle(bx, floor - s_big, s_big, s_big)
        ctx.fill()
    return n


# ---------- falling through a tunnel through the Earth ----------

R_EARTH, GM_EARTH = 6.371e6, 3.986004e14


def tunnel_sim(minutes=45):
    """Uniform-density Earth: g(r) = g0 r / R. Integrated with velocity-Verlet, 1 s steps."""
    k = GM_EARTH / R_EARTH ** 3
    x, v, out = R_EARTH, 0.0, []
    for s in range(int(minutes * 60) + 1):
        out.append((x, v))
        a = -k * x
        x = x + v + 0.5 * a
        v = v + 0.5 * (a + -k * x)
    return out


def tunnel(ctx, t_sec, sim, r=300):
    panel(ctx, (0.02, 0.025, 0.06))
    cy = CY - 40
    for frac, rgb in ((1.0, (0.20, 0.45, 0.85)), (0.985, (0.55, 0.30, 0.18)), (0.55, (0.90, 0.50, 0.15)),
                      (0.19, (1.0, 0.82, 0.35))):
        ctx.arc(CX, cy, r * frac, 0, 2 * math.pi)
        ctx.set_source_rgb(*rgb)
        ctx.fill()
    ctx.set_source_rgb(0.03, 0.03, 0.05)
    ctx.rectangle(CX - 14, cy - r - 4, 28, 2 * r + 8)
    ctx.fill()
    i = min(len(sim) - 1, max(0, int(t_sec)))
    x, v = sim[i]
    ball(ctx, CX, cy - x / R_EARTH * r, 18, (1.0, 1.0, 1.0))
    return x, v


# ---------- quiz races ----------

def drop_pair(ctx, t, thrown=False, g=1500.0, h=640, vx=420.0):
    """Two balls released together from the same height. thrown=False: heavy and light dropped side by side.
    thrown=True: one dropped, one launched sideways. Returns True once they have landed."""
    panel(ctx)
    top, floor = Y0 + 120, Y0 + 120 + h
    ctx.set_source_rgb(0.6, 0.62, 0.68)
    ctx.rectangle(X0, floor + 40, X1 - X0, 6)
    ctx.fill()
    tl = math.sqrt(2 * h / g)
    tt = min(max(t, 0.0), tl)
    y = top + 0.5 * g * tt * tt
    if thrown:
        ball(ctx, 250, y, 34, (0.36, 0.78, 0.98))
        ball(ctx, 380 + vx * tt, y, 34, (1.0, 0.5, 0.1))
    else:
        ball(ctx, 330, y, 48, (0.75, 0.78, 0.85))
        ball(ctx, 750, y, 26, (1.0, 0.5, 0.1))
    return t >= tl


def cycloid_race(ctx, t, a=230.0, g=1500.0):
    """Bead on a straight ramp vs on a cycloid between the same two points, no friction."""
    panel(ctx)
    ox, oy = X0 + 90, Y0 + 170
    th = np.linspace(0, math.pi, 400)
    cyc = np.stack([a * (th - np.sin(th)), a * (1 - np.cos(th))], 1)
    end = cyc[-1]
    line = np.stack([np.linspace(0, end[0], 400), np.linspace(0, end[1], 400)], 1)
    for path, rgb in ((line, (1.0, 0.36, 0.54)), (cyc, (0.36, 0.78, 0.98))):
        ctx.set_line_width(8)
        ctx.set_source_rgb(*rgb)
        ctx.move_to(ox + path[0, 0], oy + path[0, 1])
        for q in path[1:]:
            ctx.line_to(ox + q[0], oy + q[1])
        ctx.stroke()
    res = []
    for path, rgb in ((line, (1.0, 0.36, 0.54)), (cyc, (0.36, 0.78, 0.98))):
        p, done = _slide(path, t, g)
        ball(ctx, ox + p[0], oy + p[1], 24, rgb)
        res.append(done)
    return res


_slide_cache = {}


def _slide(path, t, g):
    key = (path.shape, float(path[-1, 0]), float(path[200, 1]))
    if key not in _slide_cache:
        seglen = np.linalg.norm(np.diff(path, axis=0), axis=1)
        s_cum = np.concatenate([[0], np.cumsum(seglen)])
        dt, s, times, ss = 1 / 600, 0.5, [0.0], [0.5]
        while s < s_cum[-1]:
            y = np.interp(s, s_cum, path[:, 1])
            s += math.sqrt(max(1e-6, 2 * g * y)) * dt
            times.append(times[-1] + dt)
            ss.append(s)
        _slide_cache[key] = (s_cum, np.array(times), np.array(ss))
    s_cum, times, ss = _slide_cache[key]
    s = np.interp(max(0, t), times, ss) if t > 0 else 0
    s = min(s, s_cum[-1])
    p = np.array([np.interp(s, s_cum, path[:, 0]), np.interp(s, s_cum, path[:, 1])])
    return p, t >= times[-1]


def pendulum_race(ctx, t, L_long=560, g=1500.0, amp=0.5):
    """Same release angle; the short one (L/4) swings back first, in half the time."""
    panel(ctx)
    top = Y0 + 90
    for px, L, rgb in ((350, L_long, (0.36, 0.78, 0.98)), (730, L_long / 4, (1.0, 0.5, 0.1))):
        w = math.sqrt(g / L)
        a = amp * math.cos(w * max(0, t))
        bx, by = px + L * math.sin(a), top + L * math.cos(a)
        ctx.set_source_rgb(0.6, 0.62, 0.68)
        ctx.rectangle(px - 60, top - 12, 120, 12)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.set_line_width(3)
        ctx.move_to(px, top)
        ctx.line_to(bx, by)
        ctx.stroke()
        ball(ctx, bx, by, 34, rgb)
