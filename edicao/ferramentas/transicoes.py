"""Transições entre pontos de mudança (troca de lugar, de hora, de clipe), desenhadas com cairo.

Cada uma cobre a tela inteira no instante do corte (assim o corte some) e conta algo da história:
  roda     roda de bicicleta que atravessa a tela pintando de marinho e volta revelando a cena nova
  rota     mapa do dia: paradas com ícones ("paradas"), o ponto anda de "de" até "para" (índices)
  relogio  varredura de relógio: ponteiros giram de "hora_de" até "hora_ate" ("08:00", "16:30")
  cortina  cortina de palco fecha com um "texto" no meio e abre
  flash    luz de palco: clarão creme com raios saindo do centro
No plano: {"tipo": "transicao", "estilo": "...", "em": <s no bruto do 1º quadro da cena nova>, ...}.
"antes"/"depois" (s) mudam quanto dura de cada lado do corte; o padrão depende do estilo.
"""
import math

import cairo

DURACAO = {"roda": (0.45, 0.45), "rota": (0.4, 0.9), "relogio": (0.45, 0.55), "cortina": (0.35, 0.75),
           "flash": (0.15, 0.4)}


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def _fonte(ctx, st, tam, corpo=True):
    fam, ital = st["corpo"] if corpo else st["titulo"]
    ctx.select_font_face(fam.replace(" Semibold", "").replace(" ExtraBold", "").replace(" SemiBold", ""),
                         cairo.FONT_SLANT_ITALIC if ital and not corpo else cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(tam)


def _centro(ctx, s, x, y, cor):
    e = ctx.text_extents(s)
    ctx.move_to(x - e.x_bearing - e.width / 2, y)
    ctx.set_source_rgb(*cor)
    ctx.show_text(s)


# ---------- roda ----------

def _roda(ctx, st, x, y, R, giro):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(giro)
    ctx.set_source_rgb(*st["fundo"])
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_line_width(R * 0.13)  # pneu
    ctx.set_source_rgb(*st["tinta"])
    ctx.arc(0, 0, R * 0.92, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_line_width(R * 0.03)  # aro
    ctx.set_source_rgb(*st["destaque"])
    ctx.arc(0, 0, R * 0.80, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_line_width(R * 0.012)  # raios cruzados, como numa roda de verdade
    ctx.set_source_rgb(*st["suave"])
    for k in range(18):
        a = k * 2 * math.pi / 18
        b = a + (0.5 if k % 2 else -0.5)
        ctx.move_to(R * 0.09 * math.cos(b), R * 0.09 * math.sin(b))
        ctx.line_to(R * 0.80 * math.cos(a), R * 0.80 * math.sin(a))
    ctx.stroke()
    ctx.set_source_rgb(*st["tinta"])
    ctx.arc(0, 0, R * 0.1, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def roda(ctx, st, e, t, W, H, c):
    R = H * 0.42
    y = H - R * 0.98
    if t <= c:  # a roda entra pela esquerda, pintando atrás de si; sai pela direita no corte
        k = ease(t / c)
        x = -R + (W + 2 * R) * k
        ctx.rectangle(0, 0, max(0.0, x), H)
    else:  # volta da esquerda, agora descobrindo a cena nova
        k = ease((t - c) / (e["ate"] - e["de"] - c))
        x = -R + (W + 2 * R) * k
        ctx.rectangle(max(0.0, x), 0, W, H)
    ctx.set_source_rgb(*st["fundo"])
    ctx.fill()
    for i in range(5):  # rastro de velocidade
        yy = y - R * 0.6 + i * R * 0.3
        ctx.set_source_rgba(*st["tinta"], 0.25)
        ctx.rectangle(x - R * 1.0 - (i % 2) * R * 0.5, yy, R * 0.6, H * 0.008)
        ctx.fill()
    _roda(ctx, st, x, y, R, x / R)


# ---------- rota ----------

def _icone(ctx, st, nome, x, y, r, cor):
    ctx.save()
    ctx.translate(x, y)
    ctx.set_source_rgb(*cor)
    ctx.set_line_width(r * 0.14)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if nome == "casa":
        ctx.move_to(-r * 0.6, -r * 0.05)
        ctx.line_to(0, -r * 0.6)
        ctx.line_to(r * 0.6, -r * 0.05)
        ctx.stroke()
        ctx.rectangle(-r * 0.42, -r * 0.1, r * 0.84, r * 0.62)
        ctx.stroke()
        ctx.rectangle(-r * 0.12, r * 0.18, r * 0.24, r * 0.34)
        ctx.fill()
    elif nome == "trampo":  # notebook
        ctx.rectangle(-r * 0.5, -r * 0.45, r * 1.0, r * 0.65)
        ctx.stroke()
        ctx.move_to(-r * 0.7, r * 0.38)
        ctx.line_to(r * 0.7, r * 0.38)
        ctx.stroke()
    elif nome == "treino":  # halter
        ctx.move_to(-r * 0.45, 0)
        ctx.line_to(r * 0.45, 0)
        ctx.stroke()
        for s in (-1, 1):
            ctx.rectangle(s * r * 0.45 - r * 0.09, -r * 0.4, r * 0.18, r * 0.8)
            ctx.fill()
            ctx.rectangle(s * r * 0.66 - r * 0.07, -r * 0.26, r * 0.14, r * 0.52)
            ctx.fill()
    elif nome == "show":  # raio
        for px, py in ((0.15, -0.65), (-0.35, 0.08), (0.02, 0.08), (-0.15, 0.65), (0.35, -0.08), (-0.02, -0.08)):
            ctx.line_to(px * r, py * r)
        ctx.close_path()
        ctx.fill()
    elif nome == "noite":  # lua
        ctx.arc(0, 0, r * 0.5, 0, 2 * math.pi)
        ctx.arc_negative(r * 0.22, -r * 0.16, r * 0.42, 2 * math.pi, 0)
        ctx.fill()
    ctx.restore()


def rota(ctx, st, e, t, W, H, c):
    dur = e["ate"] - e["de"]
    sai = dur - 0.3
    # painel diagonal entra pela esquerda e sai pela direita
    k_in, k_out = ease(t / c), ease((t - sai) / 0.3)
    inc = W * 0.25
    x1 = -inc + (W + inc) * k_in + inc  # borda direita do painel
    x0 = (W + inc) * k_out - inc  # borda esquerda (só anda na saída)
    ctx.move_to(x0, 0)
    ctx.line_to(x1, 0)
    ctx.line_to(x1 - inc, H)
    ctx.line_to(x0 - inc, H)
    ctx.close_path()
    ctx.set_source_rgb(*st["fundo"])
    ctx.fill()
    a = min(ease((t - c * 0.6) / 0.2), 1 - ease((t - sai) / 0.15))
    if a <= 0:
        return
    ctx.push_group()
    paradas = e["paradas"]
    n = len(paradas)
    y = H * 0.55
    xs = [W * 0.14 + i * (W * 0.72) / (n - 1) for i in range(n)]
    ctx.set_line_width(H * 0.008)
    ctx.set_dash([H * 0.02, H * 0.016])
    ctx.set_source_rgba(*st["suave"], 0.7)
    ctx.move_to(xs[0], y)
    ctx.line_to(xs[-1], y)
    ctx.stroke()
    ctx.set_dash([])
    de, para = e["de_parada"], e["para"]
    k = ease_out((t - c) / max(0.2, sai - c - 0.15))
    xp = xs[de] + (xs[para] - xs[de]) * k
    ctx.set_line_width(H * 0.012)  # trilha já percorrida
    ctx.set_source_rgb(*st["destaque"])
    ctx.move_to(xs[0], y)
    ctx.line_to(xp, y)
    ctx.stroke()
    r = H * 0.075
    for i, (nome, rot) in enumerate(paradas):
        feita = i < para or (i == para and k >= 1)
        ativa = i == para
        cor_fundo = st["destaque"] if feita or i <= de else st["cartao"]
        ctx.arc(xs[i], y, r * (1.18 if ativa and k >= 1 else 1.0), 0, 2 * math.pi)
        ctx.set_source_rgb(*cor_fundo)
        ctx.fill()
        _icone(ctx, st, nome, xs[i], y, r * 0.8, st["fundo"] if (feita or i <= de) else st["tinta"])
        _fonte(ctx, st, H * 0.036)
        _centro(ctx, rot.upper(), xs[i], y + r * 2.0, st["tinta"] if ativa else st["suave"])
    # o ponto que viaja (com um pulso quando chega)
    pulso = 1 + 0.25 * math.sin(min(1.0, max(0.0, (t - sai + 0.35) / 0.35)) * math.pi)
    ctx.arc(xp, y - r * 1.75, H * 0.026 * pulso, 0, 2 * math.pi)
    ctx.set_source_rgb(*st["tinta"])
    ctx.fill()
    ctx.move_to(xp - H * 0.022, y - r * 1.75 + H * 0.016)
    ctx.line_to(xp, y - r * 1.2)
    ctx.line_to(xp + H * 0.022, y - r * 1.75 + H * 0.016)
    ctx.fill()
    if e.get("texto"):
        _fonte(ctx, st, H * 0.085, corpo=False)
        _centro(ctx, e["texto"], W / 2, H * 0.3, st["tinta"])
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)


# ---------- relógio ----------

def _hora(s):
    h, m = s.split(":")
    return int(h) + int(m) / 60


def relogio(ctx, st, e, t, W, H, c):
    dur = e["ate"] - e["de"]
    cx, cy = W / 2, H / 2
    R = math.hypot(W, H)
    topo = -math.pi / 2
    if t <= c:  # setor marinho cresce no sentido horário
        ang = 2 * math.pi * ease(t / c)
        ctx.move_to(cx, cy)
        ctx.arc(cx, cy, R, topo, topo + ang)
    else:  # e continua girando, agora descobrindo
        ang = 2 * math.pi * ease((t - c) / (dur - c))
        ctx.move_to(cx, cy)
        ctx.arc(cx, cy, R, topo + ang, topo + 2 * math.pi)
    ctx.close_path()
    ctx.set_source_rgb(*st["fundo"])
    ctx.fill()
    # mostrador
    rr = H * 0.3
    a = min(1.0, t / 0.15, (dur - t) / 0.15)
    ctx.push_group()
    ctx.set_line_width(H * 0.012)
    ctx.set_source_rgb(*st["tinta"])
    ctx.arc(cx, cy, rr, 0, 2 * math.pi)
    ctx.stroke()
    for k in range(12):
        an = k * math.pi / 6
        ctx.set_line_width(H * (0.01 if k % 3 == 0 else 0.005))
        ctx.move_to(cx + rr * 0.86 * math.cos(an), cy + rr * 0.86 * math.sin(an))
        ctx.line_to(cx + rr * 0.97 * math.cos(an), cy + rr * 0.97 * math.sin(an))
        ctx.stroke()
    h0, h1 = _hora(e["hora_de"]), _hora(e["hora_ate"])
    h = h0 + (h1 - h0) * ease(t / dur)
    for comp, larg, ang, cor in ((0.5, 0.016, (h % 12) / 12 * 2 * math.pi, st["tinta"]),
                                 (0.78, 0.009, (h % 1) * 2 * math.pi, st["destaque"])):
        ctx.set_line_width(H * larg)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgb(*cor)
        ctx.move_to(cx, cy)
        ctx.line_to(cx + rr * comp * math.sin(ang), cy - rr * comp * math.cos(ang))
        ctx.stroke()
    ctx.arc(cx, cy, H * 0.015, 0, 2 * math.pi)
    ctx.fill()
    _fonte(ctx, st, H * 0.055)
    hh = int(h) % 24
    _centro(ctx, f"{hh:02d}:{int((h % 1) * 60):02d}", cx, cy + rr + H * 0.1, st["tinta"])
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(max(0.0, a))


# ---------- cortina ----------

def _pano(ctx, st, x0, x1, H, lado):
    w = x1 - x0
    if w <= 0:
        return
    g = cairo.LinearGradient(x0, 0, x1, 0)
    dobras = 7
    for i in range(dobras + 1):
        f = i / dobras
        luz = 0.75 + 0.25 * math.cos(f * dobras * math.pi)
        g.add_color_stop_rgb(f, *(c * luz for c in st["destaque"]))
    ctx.rectangle(x0, 0, w, H)
    ctx.set_source(g)
    ctx.fill()
    ctx.rectangle(x1 - 6 if lado == "esq" else x0, 0, 6, H)  # sombra da borda
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.fill()


def cortina(ctx, st, e, t, W, H, c):
    dur = e["ate"] - e["de"]
    abre = dur - 0.35
    k = ease(t / c) if t <= c else 1 - ease((t - abre) / 0.35)
    meio = W / 2 * k
    _pano(ctx, st, 0, meio + 2, H, "esq")
    _pano(ctx, st, W - meio - 2, W, H, "dir")
    ctx.rectangle(0, 0, W, H * 0.09 * min(1.0, t / 0.2))  # sanefa
    ctx.set_source_rgb(*st["fundo"])
    ctx.fill()
    a = min(ease((t - c) / 0.15), 1 - ease((t - abre) / 0.12))
    if e.get("texto") and a > 0:
        ctx.push_group()
        _fonte(ctx, st, H * 0.1, corpo=False)
        ext = ctx.text_extents(e["texto"])
        pw, ph = ext.width + H * 0.12, H * 0.18
        ctx.rectangle(W / 2 - pw / 2, H / 2 - ph / 2, pw, ph)
        ctx.set_source_rgb(*st["fundo"])
        ctx.fill()
        _centro(ctx, e["texto"], W / 2, H / 2 + H * 0.035, st["tinta"])
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)


# ---------- flash ----------

def flash(ctx, st, e, t, W, H, c):
    dur = e["ate"] - e["de"]
    k = ease(t / c) if t <= c else 1 - ease((t - c) / (dur - c))
    cx, cy = W / 2, H * 0.4
    ctx.save()
    ctx.translate(cx, cy)
    for i in range(14):  # raios de refletor girando
        ang = i * 2 * math.pi / 14 + t * 1.5
        ctx.move_to(0, 0)
        ctx.arc(0, 0, W * 1.2, ang, ang + 0.12)
        ctx.close_path()
    ctx.restore()
    ctx.set_source_rgba(*st["tinta"], 0.55 * min(1.0, k * 1.6))
    ctx.fill()
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, W * 0.9)
    g.add_color_stop_rgba(0, *st["tinta"], min(1.0, k * 1.3))
    g.add_color_stop_rgba(0.5 + 0.5 * k, *st["tinta"], k ** 1.5)
    g.add_color_stop_rgba(1, *st["tinta"], k ** 3)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()
    if t > c - 0.05 and t < c + 0.08:  # nos quadros do corte, tela toda clara
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgb(*st["tinta"])
        ctx.fill()


ESTILOS = {"roda": roda, "rota": rota, "relogio": relogio, "cortina": cortina, "flash": flash}


def desenhar(ctx, st, e, t, W, H):
    ESTILOS[e["estilo"]](ctx, st, e, t, W, H, e["corte"])


def tempos(e, corte_editado):
    """de/ate no vídeo editado em volta do corte."""
    antes, depois = DURACAO[e["estilo"]]
    antes, depois = e.get("antes", antes), e.get("depois", depois)
    return dict(e, de=corte_editado - antes, ate=corte_editado + depois, corte=antes)
