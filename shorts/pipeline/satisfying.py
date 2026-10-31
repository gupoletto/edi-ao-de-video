"""Oddly satisfying loops drawn with cairo: gears, dominoes, ball sort, perfect fit, line clear, and a ball-filling
simulation for the "how many fit?" quiz. Each draw function takes t (seconds since the scene started)."""
import math

import numpy as np

from core import AREA, round_rect
from physics import ball, panel

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2
CORES = [(0.36, 0.78, 0.98), (1.0, 0.36, 0.54), (0.30, 0.90, 0.50), (1.0, 0.85, 0.25), (0.70, 0.50, 1.0)]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ---------- gears ----------

def _gear(ctx, x, y, r, teeth, ang, rgb):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    h = r * 0.16
    for k in range(teeth * 2):
        a0 = k * math.pi / teeth
        rr = r + (h if k % 2 == 0 else 0)
        ctx.arc(0, 0, rr, a0, a0 + math.pi / teeth)
    ctx.close_path()
    ctx.set_source_rgb(*rgb)
    ctx.fill()
    ctx.arc(0, 0, r * 0.32, 0, 2 * math.pi)
    ctx.set_source_rgb(0.05, 0.06, 0.10)
    ctx.fill()
    for k in range(5):  # raios
        ctx.save()
        ctx.rotate(k * 2 * math.pi / 5)
        ctx.rectangle(r * 0.38, -r * 0.08, r * 0.42, r * 0.16)
        ctx.restore()
    ctx.set_source_rgba(0.05, 0.06, 0.10, 0.5)
    ctx.fill()
    ctx.restore()


def gears(ctx, t):
    """Three meshing gears; speeds follow the tooth ratio (24 : 12 : 18 teeth)."""
    panel(ctx)
    w = 0.9 * t
    specs = [(CX - 150, CY - 120, 230, 24, 0.0), (CX + 175, CY - 300, 115, 12, None), (CX + 160, CY + 210, 172, 18, None)]
    _gear(ctx, specs[0][0], specs[0][1], specs[0][2], 24, w, (1.0, 0.85, 0.25))
    _gear(ctx, specs[1][0], specs[1][1], specs[1][2], 12, -w * 24 / 12 + 0.13, (0.36, 0.78, 0.98))
    _gear(ctx, specs[2][0], specs[2][1], specs[2][2], 18, -w * 24 / 18 + 0.09, (1.0, 0.36, 0.54))


# ---------- dominoes (side view, three rows in a zigzag) ----------

def dominoes(ctx, t, start=0.5, por_seg=11.0, linhas=3, n=12):
    """Side view: each domino tips over its front corner and rests at ~70°, one after the other; the chain
    turns at the end of each row."""
    panel(ctx)
    w, h = 20, 120
    gap = (X1 - X0 - 160) / n
    for r in range(linhas):
        yb = Y0 + 260 + r * 320
        ctx.set_source_rgba(1, 1, 1, 0.15)
        ctx.rectangle(X0 + 50, yb, X1 - X0 - 100, 4)
        ctx.fill()
        for k in range(n):
            idx = r * n + k
            q = ease((t - start - idx / por_seg) / 0.18)
            ida = r % 2 == 0
            x = X0 + 80 + (k if ida else n - 1 - k) * gap
            ctx.save()
            ctx.translate(x + (w if ida else 0), yb)
            ctx.rotate((1 if ida else -1) * math.radians(68) * q)
            ctx.rectangle(-w if ida else 0, -h, w, h)
            ctx.restore()
            ctx.set_source_rgb(*CORES[idx % 5])
            ctx.fill()


# ---------- ball sort ----------

def _sort_moves(cap=4):
    """Tubes start mixed and are solved by the shortest legal sequence (BFS): a ball moves onto an empty tube or onto
    a ball of the same colour, never above the tube capacity. Returns (tubes, [(from, to, colour), ...])."""
    from collections import deque
    tubos = [[0, 1, 2, 0], [1, 2, 0, 1], [2, 0, 1, 2], [], []]
    inicio = tuple(tuple(tb) for tb in tubos)

    def resolvido(e):
        return all(not tb or (len(tb) == cap and len(set(tb)) == 1) for tb in e)
    fila, veio = deque([inicio]), {inicio: None}
    while fila:
        e = fila.popleft()
        if resolvido(e):
            break
        for a, ta in enumerate(e):
            if not ta:
                continue
            for b, tb in enumerate(e):
                if a == b or len(tb) >= cap or (tb and tb[-1] != ta[-1]) or (not tb and len(set(ta)) == 1):
                    continue
                n = [list(x) for x in e]
                n[b].append(n[a].pop())
                n = tuple(tuple(x) for x in n)
                if n not in veio:
                    veio[n] = (e, (a, b, ta[-1]))
                    fila.append(n)
    moves = []
    while veio[e]:
        e, mv = veio[e]
        moves.append(mv)
    return tubos, moves[::-1]


def ball_sort(ctx, t, passo=0.42):
    panel(ctx)
    tubos, moves = _sort_moves()
    estado = [list(tb) for tb in tubos]
    n = len(estado)
    r = 46
    xs = [X0 + 120 + i * ((X1 - X0 - 240) / (n - 1)) for i in range(n)]
    base = Y1 - 200
    k = min(len(moves), int(t / passo))
    for a, b, c in moves[:k]:
        estado[b].append(estado[a].pop())
    voando = None
    if k < len(moves):
        a, b, c = moves[k]
        q = (t - k * passo) / passo
        estado[a].pop()
        voando = (a, b, c, ease(q))
    for i, x in enumerate(xs):
        round_rect(ctx, x - r - 10, base - 4 * 2 * r - 30, 2 * r + 20, 4 * 2 * r + 40, 24)
        ctx.set_source_rgba(1, 1, 1, 0.12)
        ctx.fill()
        for j, c in enumerate(estado[i]):
            ball(ctx, x, base - r - j * 2 * r, r - 3, CORES[c])
        if len(estado[i]) == 4 and len(set(estado[i])) == 1:  # tubo resolvido brilha
            round_rect(ctx, x - r - 10, base - 4 * 2 * r - 30, 2 * r + 20, 4 * 2 * r + 40, 24)
            ctx.set_source_rgba(*CORES[estado[i][0]], 0.35)
            ctx.set_line_width(6)
            ctx.stroke()
    if voando:
        a, b, c, q = voando
        ya = base - r - len(estado[a]) * 2 * r
        yb = base - r - len(estado[b]) * 2 * r
        topo = base - 4 * 2 * r - 120
        x = xs[a] + (xs[b] - xs[a]) * q
        y = (1 - q) ** 2 * ya + 2 * (1 - q) * q * topo + q * q * yb
        ball(ctx, x, y, r - 3, CORES[c])


# ---------- perfect fit ----------

def _forma(ctx, tipo, x, y, s):
    if tipo == "circulo":
        ctx.arc(x, y, s, 0, 2 * math.pi)
    elif tipo == "estrela":
        for k in range(10):
            rr = s if k % 2 == 0 else s * 0.45
            a = -math.pi / 2 + k * math.pi / 5
            (ctx.line_to if k else ctx.move_to)(x + rr * math.cos(a), y + rr * math.sin(a))
        ctx.close_path()
    elif tipo == "coracao":
        ctx.move_to(x, y + s * 0.8)
        ctx.curve_to(x - s * 1.4, y - s * 0.1, x - s * 0.6, y - s * 1.1, x, y - s * 0.35)
        ctx.curve_to(x + s * 0.6, y - s * 1.1, x + s * 1.4, y - s * 0.1, x, y + s * 0.8)
        ctx.close_path()
    else:  # triangulo
        for k in range(3):
            a = -math.pi / 2 + k * 2 * math.pi / 3
            (ctx.line_to if k else ctx.move_to)(x + s * math.cos(a), y + s * math.sin(a) * 1.0)
        ctx.close_path()


def perfect_fit(ctx, t):
    panel(ctx)
    tipos = ["estrela", "coracao", "circulo", "triangulo"]
    xs = [X0 + 150 + i * ((X1 - X0 - 300) / 3) for i in range(4)]
    yb = CY + 260
    s = 78
    for i, (tp, x) in enumerate(zip(tipos, xs)):  # furos na placa
        _forma(ctx, tp, x, yb, s + 6)
        ctx.set_source_rgb(0.02, 0.02, 0.04)
        ctx.fill()
    for i, (tp, x) in enumerate(zip(tipos, xs)):
        q = ease((t - 0.5 - i * 1.1) / 0.8)
        y = (CY - 380) + (yb - (CY - 380)) * q
        ang = (1 - q) * (0.8 if i % 2 else -0.8)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(ang)
        _forma(ctx, tp, 0, 0, s)
        ctx.restore()
        ctx.set_source_rgb(*CORES[i])
        ctx.fill()
        if 0.98 < q and t - 0.5 - i * 1.1 - 0.8 < 0.25:  # "clique": anel que se abre
            k = (t - 0.5 - i * 1.1 - 0.8) / 0.25
            ctx.arc(x, yb, s + 20 + 40 * k, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - k))
            ctx.set_line_width(5)
            ctx.stroke()


# ---------- line clear ----------

def line_clear(ctx, t, cols=10, rows=14):
    """Blocks fall into a well until rows complete, flash, and vanish; the stack drops into place."""
    panel(ctx)
    cel = (X1 - X0 - 160) / cols
    x0 = CX - cols * cel / 2
    yb = Y1 - 90
    rng = np.random.default_rng(5)
    gaps = rng.integers(0, cols, 4)
    # 4 linhas quase cheias; uma peça cai em cada buraco, uma linha por vez
    queda = [ease((t - 0.6 - k * 0.9) / 0.6) for k in range(4)]
    limpou = [t > 0.6 + k * 0.9 + 0.75 for k in range(4)]
    flash = [max(0.0, 1 - abs(t - (0.6 + k * 0.9 + 0.65)) / 0.12) for k in range(4)]
    desce = sum(limpou)
    for r in range(4):
        if limpou[r]:
            continue
        y = yb - (r - sum(limpou[:r]) + 1) * cel
        for c in range(cols):
            if c == gaps[r] and queda[r] < 1:
                continue
            round_rect(ctx, x0 + c * cel + 3, y + 3, cel - 6, cel - 6, 8)
            ctx.set_source_rgb(*CORES[(r + c) % 5])
            ctx.fill()
        if flash[r] > 0:
            ctx.rectangle(x0, y, cols * cel, cel)
            ctx.set_source_rgba(1, 1, 1, flash[r])
            ctx.fill()
    for r in range(4):
        if 0 < queda[r] < 1:
            y_alvo = yb - (r - sum(limpou[:r]) + 1) * cel
            y = Y0 + 40 + (y_alvo - Y0 - 40) * queda[r]
            round_rect(ctx, x0 + gaps[r] * cel + 3, y + 3, cel - 6, cel - 6, 8)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.15)
    ctx.set_line_width(4)
    ctx.rectangle(x0 - 4, Y0 + 30, cols * cel + 8, yb - Y0 - 30)
    ctx.stroke()
    return desce


# ---------- fill a container with balls (quiz) ----------

def fill_sim(forma, r, n_max, dur=6.0, fps=30, seed=1):
    """Balls of radius r drop into a container until it is full to the rim; simple position-based physics.
    forma: "copo" (glass), "taca" (bowl) or "funil" (V). Returns (frames, count) with frames[i] = list of (x, y)."""
    rng = np.random.default_rng(seed)
    w = 520
    topo, fundo = CY - 330, CY + 330

    def parede(y):  # meia largura interna na altura y
        q = (y - topo) / (fundo - topo)
        if forma == "copo":
            return w / 2 * (1 - 0.18 * q)
        if forma == "taca":
            return w / 2 * math.sqrt(max(0.0, 1 - q * q)) + 1
        return w / 2 * (1 - q) + r * 1.1  # funil
    pos = np.zeros((0, 2))
    vel = np.zeros((0, 2))
    frames = []
    dt = 1.0 / fps / 4
    total = int(dur * fps)
    solta = np.linspace(0, dur * 0.75, n_max)
    for f in range(total):
        for sub in range(4):
            tt = (f * 4 + sub) * dt
            cheio = len(pos) > 8 and (np.abs(vel[:, 1]) < 60).all() and pos[:, 1].min() < topo + r * 1.2
            while len(pos) < n_max and solta[len(pos)] <= tt and not cheio:
                pos = np.vstack([pos, [CX + rng.uniform(-90, 90), topo - 120 - rng.uniform(0, 40)]])
                vel = np.vstack([vel, [0, 0]])
            if not len(pos):
                continue
            vel[:, 1] += 2600 * dt
            pos += vel * dt
            for _ in range(8):  # colisões entre bolas
                d = pos[:, None, :] - pos[None, :, :]
                dist = np.sqrt((d ** 2).sum(-1)) + np.eye(len(pos)) * 1e9 + 1e-6
                over = np.clip(2 * r - dist, 0, None)
                push = (d / dist[..., None]) * (over[..., None] / 2)
                pos += push.sum(1)
            for i in range(len(pos)):  # paredes e fundo
                x, y = pos[i]
                if y > fundo - r:
                    pos[i, 1] = fundo - r
                    vel[i, 1] *= -0.2
                hw = parede(min(max(y, topo), fundo)) - r
                if y > topo and abs(x - CX) > hw:
                    pos[i, 0] = CX + math.copysign(max(hw, 0), x - CX)
                    vel[i, 0] *= -0.3
            vel *= 0.995
        frames.append(pos.copy())
    final = frames[-1]
    dentro = int(((final[:, 1] > topo - r) & (final[:, 1] < fundo)).sum())
    return frames, dentro, (topo, fundo, parede)


def draw_fill(ctx, t, sim, r, mostrar=True, cor=(0.36, 0.78, 0.98)):
    panel(ctx)
    frames, n, (topo, fundo, parede) = sim
    ys = np.linspace(topo, fundo, 40)
    ctx.set_line_width(8)
    ctx.set_source_rgba(1, 1, 1, 0.85)
    for sinal in (-1, 1):
        for i, y in enumerate(ys):
            (ctx.line_to if i else ctx.move_to)(CX + sinal * (parede(y) + 4), y)
        ctx.stroke()
    ctx.move_to(CX - parede(fundo) - 4, fundo + 4)
    ctx.line_to(CX + parede(fundo) + 4, fundo + 4)
    ctx.stroke()
    if mostrar:
        f = min(len(frames) - 1, int(t * 30))
        for i, (x, y) in enumerate(frames[f]):
            ball(ctx, x, y, r - 1, CORES[i % 5] if cor is None else cor)


def capacidade(forma, r, n0, dur=6.2, tentativas=6):
    """Simula de novo até toda bola solta caber no recipiente; devolve a simulação em que a resposta do quiz
    (sim[1]) é exatamente o número de bolas na tela. Use no lugar de fill_sim nos quizzes."""
    n = n0
    for _ in range(tentativas):
        sim = fill_sim(forma, r, n, dur=dur)
        if sim[1] == len(sim[0][-1]):
            return sim
        n = sim[1]
    raise RuntimeError(f"{forma}: a capacidade não convergiu ({n})")
