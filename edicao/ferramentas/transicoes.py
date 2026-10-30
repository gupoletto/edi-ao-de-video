"""Transições entre pontos de mudança (troca de lugar, de hora, de clipe), desenhadas com cairo.

Cada uma cobre a tela inteira no instante do corte (assim o corte some) e conta algo da história:
  roda     roda de bicicleta que atravessa a tela pintando de marinho e volta revelando a cena nova
  rota     mapa do dia: paradas com ícones ("paradas"), o ponto anda de "de" até "para" (índices)
  relogio  varredura de relógio: ponteiros giram de "hora_de" até "hora_ate" ("08:00", "16:30")
  cortina  cortina de palco fecha com um "texto" no meio e abre
  flash    luz de palco: clarão creme com raios saindo do centro
  blocos   grade de quadrados que acende em onda diagonal (pixels) e apaga
  tinta    respingo de tinta que cobre tudo e abre um buraco orgânico ("x", "y" do respingo; "cor": "taupe")
  glitch   falha digital com faixas deslocadas e blocos; "texto" opcional quebrado em RGB
  papel    folha creme rasgada que passa pela tela; "texto" opcional escrito nela
  iris     círculo de desenho animado fecha num ponto ("x", "y", padrão o rosto) e abre
  persiana lâminas verticais que giram e fecham, uma após a outra
  filme    contagem de filme antigo 3-2-1 ("contagem") com grão e riscos
  celular  um celular sobe e vira a tela: tela de bloqueio com "hora", "data" e notificação ("app", "texto")
  polaroid polaroid cai com legenda escrita à mão ("texto") e a cena nova aparece de dentro da foto
  cronometro relógio de corrida: "km" contando, "pace", "rotulo"
  cupom    cupom de mercado impresso: "itens" [..], "total", "titulo"
  anilhas  duas anilhas de academia fecham a tela, com "texto"
  vapor    vapor de comida quente cobre e se desfaz, com "texto"
  rebobinar fita VHS rebobinando: "de_hora" -> "para_hora", "rotulo", "texto"
No plano: {"tipo": "transicao", "estilo": "...", "em": <s no bruto do 1º quadro da cena nova>, ...}.
"antes"/"depois" (s) mudam quanto dura de cada lado do corte; o padrão depende do estilo.
"""
import math

import cairo

DURACAO = {"roda": (0.45, 0.45), "rota": (0.4, 0.9), "relogio": (0.45, 0.55), "cortina": (0.35, 0.75),
           "flash": (0.15, 0.4), "blocos": (0.4, 0.45), "tinta": (0.35, 0.45), "glitch": (0.3, 0.3),
           "papel": (0.35, 0.45), "iris": (0.4, 0.45), "persiana": (0.35, 0.4), "filme": (0.9, 0.25),
           "celular": (0.5, 1.0), "polaroid": (0.45, 0.8), "cronometro": (0.45, 1.1), "cupom": (0.45, 1.4),
           "anilhas": (0.4, 0.7), "vapor": (0.4, 0.7), "rebobinar": (0.7, 0.5)}


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


# ---------- blocos ----------

def blocos(ctx, st, e, t, W, H, c):
    """Grade de quadrados que acendem em onda diagonal (como pixels) e apagam na mesma direção."""
    dur = e["ate"] - e["de"]
    n_col = 16
    lado = W / n_col
    n_lin = int(math.ceil(H / lado))
    cores = (st["fundo"], st["cartao"], st["destaque"])
    for i in range(n_col):
        for j in range(n_lin):
            ordem = (i + j) / (n_col + n_lin - 2)  # 0 no canto de cima à esquerda, 1 no de baixo à direita
            if t <= c:
                k = ease((t / c - ordem * 0.6) / 0.4)
            else:
                k = 1 - ease(((t - c) / (dur - c) - ordem * 0.6) / 0.4)
            if k <= 0:
                continue
            m = lado * k
            ctx.rectangle(i * lado + (lado - m) / 2, j * lado + (lado - m) / 2, m + 0.6, m + 0.6)
            cor = cores[0] if k >= 0.999 else cores[(i * 7 + j * 3) % 3]
            ctx.set_source_rgb(*cor)
            ctx.fill()


# ---------- tinta ----------

def _mancha(ctx, cx, cy, r, semente):
    """Contorno de mancha de tinta: círculo com ondulações suaves de várias frequências."""
    fases = [semente * 1.7 + k for k in range(4)]
    for k in range(96):
        a = k * 2 * math.pi / 96
        rr = r * (1 + 0.10 * math.sin(3 * a + fases[0]) + 0.07 * math.sin(5 * a + fases[1])
                  + 0.04 * math.sin(11 * a + fases[2]) + 0.025 * math.sin(17 * a + fases[3]))
        (ctx.line_to if k else ctx.move_to)(cx + rr * math.cos(a), cy + rr * math.sin(a))
    ctx.close_path()


def tinta(ctx, st, e, t, W, H, c):
    """Respingo de tinta: uma mancha orgânica cresce de um ponto até cobrir tudo, com gotas em volta; na volta,
    um buraco com a mesma borda se abre no meio e revela a cena nova."""
    dur = e["ate"] - e["de"]
    cx, cy = W * e.get("x", 0.62), H * e.get("y", 0.45)
    Rmax = math.hypot(W, H) * 0.75
    cor = st["destaque"] if e.get("cor") == "taupe" else st["fundo"]
    if t <= c:
        r = Rmax * ease_out(t / c) ** 1.2
        _mancha(ctx, cx, cy, r, 3)
        ctx.set_source_rgb(*cor)
        ctx.fill()
        for g in range(9):  # gotas que voam na frente
            a = g * 2.3
            d = r * (1.15 + 0.25 * (g % 3))
            ctx.arc(cx + d * math.cos(a), cy + d * math.sin(a), H * 0.012 * (1 + g % 3) * ease(t / c * 2), 0, 2 * math.pi)
            ctx.fill()
    else:
        r = Rmax * ease((t - c) / (dur - c))
        ctx.rectangle(0, 0, W, H)
        _mancha(ctx, W / 2, H / 2, r, 5)
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        ctx.set_source_rgb(*cor)
        ctx.fill()
        ctx.set_fill_rule(cairo.FILL_RULE_WINDING)


# ---------- glitch ----------

def glitch(ctx, st, e, t, W, H, c):
    """Falha digital: faixas horizontais deslocadas em marinho/creme/taupe, ruído de blocos e um quadro cheio no corte."""
    dur = e["ate"] - e["de"]
    rnd = __import__("random").Random(int(t * 30) * 13 + 1)
    perto = 1 - min(1.0, abs(t - c) / max(c, dur - c))  # 0 longe do corte, 1 no corte
    if abs(t - c) < 0.07:
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgb(*st["fundo"])
        ctx.fill()
    n = int(4 + 22 * perto)
    for _ in range(n):
        y = rnd.uniform(0, H)
        h = rnd.uniform(H * 0.01, H * 0.09) * (0.5 + perto)
        x = rnd.uniform(-W * 0.3, W * 0.6)
        w = rnd.uniform(W * 0.2, W * 0.9)
        cor = rnd.choice([st["fundo"], st["fundo"], st["tinta"], st["destaque"], st["suave"]])
        ctx.rectangle(x, y, w, h)
        ctx.set_source_rgba(*cor, 0.55 + 0.45 * perto)
        ctx.fill()
    for _ in range(int(40 * perto)):  # blocos de compressão
        s = rnd.uniform(8, 28)
        ctx.rectangle(rnd.uniform(0, W), rnd.uniform(0, H), s, s)
        ctx.set_source_rgba(*rnd.choice([st["tinta"], st["destaque"]]), 0.8)
        ctx.fill()
    if e.get("texto") and abs(t - c) < 0.35:  # texto "quebrado" em três cópias deslocadas
        _fonte(ctx, st, H * 0.12)
        for dx, cor, a in ((-8, st["destaque"], 0.8), (8, st["suave"], 0.8), (0, st["tinta"], 1.0)):
            ctx.save()
            ctx.translate(dx * (1 + rnd.random()), 0)
            ctx.set_source_rgba(*cor, a)
            ext = ctx.text_extents(e["texto"])
            ctx.move_to(W / 2 - ext.width / 2 - ext.x_bearing, H / 2 + ext.height / 2)
            ctx.show_text(e["texto"])
            ctx.restore()


# ---------- papel ----------

def _borda_rasgada(x, H, semente, amp):
    rng = __import__("random").Random(semente)
    pts, y = [], -10.0
    while y < H + 10:
        pts.append((x + rng.uniform(-amp, amp), y))
        y += rng.uniform(H * 0.015, H * 0.045)
    return pts


def papel(ctx, st, e, t, W, H, c):
    """Folha de papel creme entra rasgada pela direita (com sombra) e sai rasgando para a esquerda."""
    dur = e["ate"] - e["de"]
    amp = W * 0.018
    if t <= c:
        x = W * 1.05 - (W * 1.1) * ease(t / c)
        borda, cobre_dir = _borda_rasgada(x, H, 11, amp), True
    else:
        x = W * 1.05 - (W * 1.1) * ease((t - c) / (dur - c))
        borda, cobre_dir = _borda_rasgada(x, H, 12, amp), False
    for sombra, cor, a in ((14, (0, 0, 0), 0.25), (0, st["tinta"], 1.0)):
        ctx.move_to(borda[0][0] - sombra, borda[0][1])
        for px, py in borda:
            ctx.line_to(px - sombra, py)
        lado = W + 50 if cobre_dir else -50
        ctx.line_to(lado, H + 10)
        ctx.line_to(lado, -10)
        ctx.close_path()
        ctx.set_source_rgba(*cor, a)
        ctx.fill()
    # fibras da borda
    ctx.set_line_width(2)
    ctx.set_source_rgba(*st["suave"], 0.6)
    for px, py in borda[::2]:
        ctx.move_to(px, py)
        ctx.line_to(px + (8 if cobre_dir else -8), py + 4)
    ctx.stroke()
    if e.get("texto") and abs(t - c) < 0.3:
        _fonte(ctx, st, H * 0.1, corpo=False)
        _centro(ctx, e["texto"], W / 2, H / 2 + H * 0.035, st["fundo"])


# ---------- íris ----------

def iris(ctx, st, e, t, W, H, c):
    """Íris de desenho animado: um círculo fecha sobre um ponto (o rosto), fica preto um instante e abre."""
    dur = e["ate"] - e["de"]
    cx, cy = W * e.get("x", 0.5), H * e.get("y", 0.42)
    Rmax = math.hypot(W, H)
    if t <= c:
        r = Rmax * (1 - ease(t / c))
    else:
        r = Rmax * ease((t - c - 0.08) / (dur - c - 0.08)) if t > c + 0.08 else 0
    ctx.rectangle(0, 0, W, H)
    if r > 0:
        ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.set_source_rgb(*st["fundo"])
    ctx.fill()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    if r > 0:
        ctx.set_line_width(H * 0.012)
        ctx.set_source_rgb(*st["destaque"])
        ctx.arc(cx, cy, r, 0, 2 * math.pi)
        ctx.stroke()


# ---------- persiana ----------

def persiana(ctx, st, e, t, W, H, c):
    """Lâminas verticais que giram (ficam mais largas) até fechar e depois abrem, uma atrás da outra."""
    dur = e["ate"] - e["de"]
    n = 10
    w = W / n
    for i in range(n):
        atraso = i / n * 0.45
        if t <= c:
            k = ease((t / c - atraso) / 0.55)
        else:
            k = 1 - ease(((t - c) / (dur - c) - atraso) / 0.55)
        if k <= 0:
            continue
        lw = w * k
        x = i * w + (w - lw) / 2
        g = cairo.LinearGradient(x, 0, x + lw, 0)
        g.add_color_stop_rgb(0, *(v * 0.75 for v in st["cartao"]))
        g.add_color_stop_rgb(0.5, *st["cartao"])
        g.add_color_stop_rgb(1, *st["fundo"])
        ctx.rectangle(x, 0, lw + 0.8, H)
        ctx.set_source(g if k < 0.999 else cairo.SolidPattern(*st["fundo"]))
        ctx.fill()


# ---------- filme ----------

def filme(ctx, st, e, t, W, H, c):
    """Contagem de filme antigo (3, 2, 1) com o ponteiro varrendo, grão e riscos; no corte, quadro cheio."""
    dur = e["ate"] - e["de"]
    a = min(1.0, t / 0.12, (dur - t) / 0.18)
    if a <= 0:
        return
    ctx.push_group()
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(*(v * 0.9 for v in st["tinta"]))
    ctx.fill()
    cx, cy, R = W / 2, H / 2, H * 0.36
    n0 = e.get("contagem", 3)
    passo = c / n0 if c > 0 else 1
    k = int(t / passo)
    frac = (t % passo) / passo
    num = max(1, n0 - k) if t < c else 1
    ctx.move_to(cx, cy)  # setor que varre
    ctx.arc(cx, cy, R * 1.6, -math.pi / 2, -math.pi / 2 + 2 * math.pi * (frac if t < c else 1))
    ctx.close_path()
    ctx.set_source_rgba(*st["suave"], 0.55)
    ctx.fill()
    ctx.set_source_rgb(*st["fundo"])
    ctx.set_line_width(H * 0.008)
    for rr in (R, R * 0.82):
        ctx.arc(cx, cy, rr, 0, 2 * math.pi)
        ctx.stroke()
    ctx.move_to(0, cy)
    ctx.line_to(W, cy)
    ctx.move_to(cx, 0)
    ctx.line_to(cx, H)
    ctx.stroke()
    _fonte(ctx, st, H * 0.42)
    _centro(ctx, str(num), cx, cy + H * 0.15, st["fundo"])
    rnd = __import__("random").Random(int(t * 24))
    for _ in range(3):  # riscos e poeira
        x = rnd.uniform(0, W)
        ctx.move_to(x, 0)
        ctx.line_to(x + rnd.uniform(-20, 20), H)
        ctx.set_line_width(rnd.uniform(1, 3))
        ctx.set_source_rgba(0, 0, 0, 0.25)
        ctx.stroke()
    for _ in range(25):
        ctx.arc(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 4), 0, 2 * math.pi)
        ctx.set_source_rgba(0, 0, 0, 0.3)
        ctx.fill()
    vin = cairo.RadialGradient(cx, cy, H * 0.3, cx, cy, W * 0.7)  # vinheta escura nas bordas
    vin.add_color_stop_rgba(0, 0, 0, 0, 0)
    vin.add_color_stop_rgba(1, 0, 0, 0, 0.5)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vin)
    ctx.fill()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)


# ---------- celular ----------

def celular(ctx, st, e, t, W, H, c):
    """Um celular sobe da parte de baixo e cresce até a tela dele virar a tela do vídeo: tela de bloqueio com a hora
    ("hora") e uma notificação ("texto", "app"); depois desce e revela a cena nova."""
    dur = e["ate"] - e["de"]
    if t <= c:
        k = ease(t / c)
    else:
        k = 1 - ease((t - c - 0.35) / (dur - c - 0.35)) if t > c + 0.35 else 1.0
    # tamanho: de um celular na mão (0) até a tela cheia (1)
    pw0, ph0 = H * 0.42, H * 0.86
    s = 1 + (max(W / (pw0 * 0.92), H / (ph0 * 0.94)) - 1) * ease((k - 0.45) / 0.55)
    y_off = H * 1.1 * (1 - ease(k / 0.45))
    cx, cy = W / 2, H / 2 + y_off
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    pw, ph = pw0, ph0
    r = pw * 0.12
    _ret(ctx, -pw / 2, -ph / 2, pw, ph, r)
    ctx.set_source_rgb(0.06, 0.06, 0.08)
    ctx.fill()
    sw, sh = pw * 0.92, ph * 0.94
    _ret(ctx, -sw / 2, -sh / 2, sw, sh, r * 0.8)
    g = cairo.LinearGradient(0, -sh / 2, 0, sh / 2)
    g.add_color_stop_rgb(0, *st["cartao"])
    g.add_color_stop_rgb(1, *st["fundo"])
    ctx.set_source(g)
    ctx.fill()
    _fonte(ctx, st, sh * 0.13)
    _centro(ctx, e.get("hora", "07:00"), 0, -sh * 0.22, st["tinta"])
    _fonte(ctx, st, sh * 0.03)
    _centro(ctx, e.get("data", "quinta-feira"), 0, -sh * 0.33, st["suave"])
    na = ease((t - c * 0.7) / 0.25) if t > c * 0.7 else 0  # a notificação cai do topo
    if na > 0 and e.get("texto"):
        nw, nh = sw * 0.92, sh * 0.12
        ny = -sh * 0.08 - (1 - na) * sh * 0.2
        ctx.push_group()
        _ret(ctx, -nw / 2, ny, nw, nh, nh * 0.25)
        ctx.set_source_rgba(*st["tinta"], 0.95)
        ctx.fill()
        ctx.arc(-nw / 2 + nh * 0.5, ny + nh / 2, nh * 0.28, 0, 2 * math.pi)
        ctx.set_source_rgb(*st["destaque"])
        ctx.fill()
        _fonte(ctx, st, nh * 0.22)
        ctx.move_to(-nw / 2 + nh * 0.95, ny + nh * 0.42)
        ctx.set_source_rgb(*st["suave"])
        ctx.show_text(e.get("app", "LEMBRETE").upper())
        tam = nh * 0.27
        _fonte(ctx, st, tam)
        livre = nw - nh * 1.2
        if ctx.text_extents(e["texto"]).x_advance > livre:  # encolhe o texto para caber na notificação
            tam *= livre / ctx.text_extents(e["texto"]).x_advance
            _fonte(ctx, st, tam)
        ctx.move_to(-nw / 2 + nh * 0.95, ny + nh * 0.78)
        ctx.set_source_rgb(*st["fundo"])
        ctx.show_text(e["texto"])
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(na)
    ctx.restore()
    if s > 1.5:  # quando o celular passa da tela, o fundo fora dele também fica marinho
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgba(*st["fundo"], min(1.0, (s - 1.5)))
        ctx.set_operator(cairo.OPERATOR_DEST_OVER)
        ctx.fill()
        ctx.set_operator(cairo.OPERATOR_OVER)


def _ret(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


# ---------- polaroid ----------

def polaroid(ctx, st, e, t, W, H, c):
    """Uma polaroid cai girando sobre um fundo marinho com a legenda escrita ("texto"), e a cena nova aparece de dentro
    da foto: a moldura cresce até sair da tela."""
    dur = e["ate"] - e["de"]
    if t <= c:  # fundo marinho entra em cortina rápida de cima
        ctx.rectangle(0, 0, W, H * ease(t / c))
        ctx.set_source_rgb(*st["fundo"])
        ctx.fill()
        cai = ease_out(t / c)
        z, ang, oy = 1.0, math.radians(-18 + 12 * cai), -H * (1 - cai)
        foto_a = 0.0
    else:
        q = (t - c) / (dur - c)
        z = 1 + 4.5 * ease((q - 0.35) / 0.65) ** 2
        ang, oy = math.radians(-6 * (1 - ease(q / 0.6))), 0
        foto_a = 1.0
        # fora da polaroid continua marinho até ela crescer
        ctx.rectangle(0, 0, W, H)
        fw, fh = H * 0.62 * z, H * 0.74 * z
        ctx.save()
        ctx.translate(W / 2, H / 2)
        ctx.rotate(ang)
        ctx.rectangle(-fw / 2, -fh / 2, fw, fh)
        ctx.restore()
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        ctx.set_source_rgb(*st["fundo"])
        ctx.fill()
        ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    fw, fh = H * 0.62 * z, H * 0.74 * z
    ctx.save()
    ctx.translate(W / 2, H / 2 + oy)
    ctx.rotate(ang)
    # moldura (com a janela da foto vazada quando a cena nova aparece)
    ctx.rectangle(-fw / 2, -fh / 2, fw, fh)
    jw = fw * 0.88
    jy0 = -fh / 2 + fw * 0.06
    if foto_a:
        ctx.rectangle(-jw / 2, jy0, jw, jw)
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.set_source_rgb(*st["tinta"])
    ctx.fill()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    if not foto_a:  # foto ainda "revelando": cinza que clareia
        ctx.rectangle(-jw / 2, jy0, jw, jw)
        ctx.set_source_rgb(*st["cartao"])
        ctx.fill()
    if e.get("texto"):
        ctx.select_font_face("Source Serif 4", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(fh * 0.075)
        ext = ctx.text_extents(e["texto"])
        ctx.move_to(-ext.width / 2 - ext.x_bearing, jy0 + jw + (fh / 2 - jy0 - jw) * 0.62 + fh * 0.035)
        ctx.set_source_rgb(*st["fundo"])
        ctx.show_text(e["texto"])
    ctx.restore()



# ---------- cronômetro (relógio de corrida) ----------

def cronometro(ctx, st, e, t, W, H, c):
    """Relógio esportivo que sobe e cresce até a tela: distância contando até "km", ritmo ("pace") e tempo;
    depois encolhe e sai. Campos: "km" (ex.: 2.0), "pace" (ex.: "5:10/km"), "rotulo" (ex.: "CORRIDA")."""
    dur = e["ate"] - e["de"]
    k = ease(t / c) if t <= c else 1 - ease((t - c - 0.45) / max(0.1, dur - c - 0.45)) if t > c + 0.45 else 1.0
    ctx.rectangle(0, 0, W, H * k)
    ctx.set_source_rgb(*st["fundo"])
    ctx.fill()
    s = 0.35 + 0.65 * ease_out(k)
    cx, cy = W / 2, H / 2 + H * (1 - ease_out(k)) * 0.6
    R = H * 0.36 * s
    ctx.save()
    ctx.translate(cx, cy)
    for sy in (-1, 1):  # pulseira
        ctx.rectangle(-R * 0.55, sy * R * 0.7, R * 1.1, sy * H)
        ctx.set_source_rgb(*st["cartao"])
        ctx.fill()
    ctx.arc(0, 0, R * 1.08, 0, 2 * math.pi)
    ctx.set_source_rgb(*st["suave"])
    ctx.fill()
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    ctx.set_source_rgb(0.02, 0.03, 0.06)
    ctx.fill()
    prog = ease_out(min(1.0, t / (c + 0.35)))
    ctx.set_line_width(R * 0.07)  # anel de progresso
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgb(*st["destaque"])
    ctx.arc(0, 0, R * 0.88, -math.pi / 2, -math.pi / 2 + 2 * math.pi * max(0.001, prog))
    ctx.stroke()
    _fonte(ctx, st, R * 0.13)
    _centro(ctx, e.get("rotulo", "CORRIDA"), 0, -R * 0.42, st["suave"])
    _fonte(ctx, st, R * 0.42)
    km = e.get("km", 2.0) * prog
    _centro(ctx, f"{km:.2f}".replace(".", ","), 0, R * 0.12, st["tinta"])
    _fonte(ctx, st, R * 0.12)
    _centro(ctx, "KM", 0, R * 0.32, st["suave"])
    if e.get("pace"):
        _fonte(ctx, st, R * 0.13)
        _centro(ctx, "PACE " + e["pace"], 0, R * 0.58, st["destaque"])
    ctx.restore()


# ---------- cupom (nota de mercado) ----------

def cupom(ctx, st, e, t, W, H, c):
    """Cupom fiscal sai da impressora de cima para baixo, com "itens" impressos um por um e o "total" (texto), e
    é puxado para cima revelando a cena nova."""
    dur = e["ate"] - e["de"]
    itens = e.get("itens", [])
    larg = W * 0.4
    x0 = W / 2 - larg / 2
    if t <= c:
        ctx.rectangle(0, 0, W, H * ease(t / c))  # o fundo desce junto
        ctx.set_source_rgb(*st["fundo"])
        ctx.fill()
        desce = ease_out(t / c)
        sobe = 0.0
    else:
        q = (t - c) / (dur - c)
        ctx.rectangle(0, 0, W, H * (1 - ease((q - 0.7) / 0.3)))
        ctx.set_source_rgb(*st["fundo"])
        ctx.fill()
        desce, sobe = 1.0, ease((q - 0.72) / 0.28)
    alto = H * 1.05
    y_fim = -alto + alto * desce - alto * 1.1 * sobe
    ctx.save()
    ctx.translate(0, y_fim + H * 0.02)
    # papel com picote de dente embaixo
    ctx.move_to(x0, 0)
    ctx.line_to(x0 + larg, 0)
    n = 18
    for i in range(n + 1):
        ctx.line_to(x0 + larg - i * larg / n, alto - (12 if i % 2 else 0))
    ctx.close_path()
    ctx.set_source_rgb(*st["tinta"])
    ctx.fill()
    ctx.select_font_face("DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    tam = H * 0.044
    ctx.set_font_size(tam)
    y = alto * 0.1
    ctx.set_source_rgb(*st["fundo"])
    _mono_c(ctx, e.get("titulo", "CUPOM DO DIA"), W / 2, y)
    y += tam * 1.4
    _mono_c(ctx, "-" * 22, W / 2, y)
    for i, it in enumerate(itens):
        y += tam * 1.6
        aparece = t > c * 0.4 + i * 0.12
        if aparece:
            ctx.move_to(x0 + larg * 0.08, y)
            ctx.show_text(it.upper()[:18])
            ctx.move_to(x0 + larg * 0.82, y)
            ctx.show_text("1x")
    y += tam * 1.6
    _mono_c(ctx, "-" * 22, W / 2, y)
    if e.get("total") and t > c * 0.4 + len(itens) * 0.12:
        y += tam * 1.8
        ctx.set_font_size(tam * 1.25)
        _mono_c(ctx, e["total"].upper(), W / 2, y)
        ctx.set_font_size(tam)
    y += tam * 2.2
    for i in range(30):  # código de barras
        w = (1 + (i * 7) % 3) * W * 0.0018
        ctx.rectangle(x0 + larg * 0.15 + i * larg * 0.0235, y, w, tam * 2)
    ctx.fill()
    ctx.restore()


def _mono_c(ctx, s, x, y):
    e = ctx.text_extents(s)
    ctx.move_to(x - e.x_advance / 2, y)
    ctx.show_text(s)


# ---------- anilhas ----------

def _anilha(ctx, st, x, y, R, giro):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(giro)
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    ctx.set_source_rgb(0.09, 0.1, 0.13)
    ctx.fill()
    ctx.set_line_width(R * 0.05)
    ctx.set_source_rgb(0.2, 0.22, 0.27)
    for rr in (0.92, 0.6):
        ctx.arc(0, 0, R * rr, 0, 2 * math.pi)
        ctx.stroke()
    _fonte(ctx, st, R * 0.22)
    for k in range(2):
        ctx.save()
        ctx.rotate(k * math.pi)
        _centro(ctx, "20 KG", 0, -R * 0.68, st["destaque"])
        ctx.restore()
    ctx.arc(0, 0, R * 0.16, 0, 2 * math.pi)
    ctx.set_source_rgb(*st["suave"])
    ctx.fill()
    ctx.arc(0, 0, R * 0.09, 0, 2 * math.pi)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    ctx.restore()


def anilhas(ctx, st, e, t, W, H, c):
    """Duas anilhas rolam das laterais e se encontram no meio (o fundo fecha atrás delas), com uma barra e o
    "texto" (ex.: "TREINO DE BRAÇO"); depois rolam de volta para fora."""
    dur = e["ate"] - e["de"]
    k = ease(t / c) if t <= c else 1 - ease((t - c - 0.3) / max(0.1, dur - c - 0.3)) if t > c + 0.3 else 1.0
    R = H * 0.62
    xl = -R + (W / 2 - R * 0.0 + R) * k - R * 0.02
    xr = W + R - (W / 2 + R) * k + R * 0.02
    ctx.rectangle(0, 0, max(0.0, xl), H)
    ctx.rectangle(min(W, xr), 0, W, H)
    ctx.set_source_rgb(*st["fundo"])
    ctx.fill()
    ctx.rectangle(0, H / 2 - H * 0.03, W, H * 0.06)  # barra
    ctx.set_source_rgba(*st["suave"], 0.9 * k)
    ctx.fill()
    _anilha(ctx, st, xl, H / 2, R, xl / R)
    _anilha(ctx, st, xr, H / 2, R, -xr / R)
    if e.get("texto") and k > 0.95:
        _fonte(ctx, st, H * 0.075)
        ext = ctx.text_extents(e["texto"])
        ctx.rectangle(W / 2 - ext.width / 2 - H * 0.04, H * 0.82, ext.width + H * 0.08, H * 0.11)
        ctx.set_source_rgb(*st["fundo"])
        ctx.fill()
        _centro(ctx, e["texto"], W / 2, H * 0.9, st["tinta"])


# ---------- vapor ----------

def vapor(ctx, st, e, t, W, H, c):
    """Nuvens de vapor (comida quente) sobem de baixo, tomam a tela e se desfazem para cima com o "texto"."""
    dur = e["ate"] - e["de"]
    rnd = __import__("random").Random(9)
    bolhas = [(rnd.uniform(-0.1, 1.1), rnd.uniform(0.0, 1.0), rnd.uniform(0.18, 0.4), rnd.uniform(0, 6)) for _ in range(60)]
    if t <= c:
        sob = ease(t / c)
        dissolve = 0.0
    else:
        sob = 1.0 + 0.6 * ease((t - c) / (dur - c))
        dissolve = ease((t - c - 0.2) / max(0.1, dur - c - 0.2))
    for bx, by, br, fase in bolhas:
        y = H * (1.4 - by * 0.9) - H * 1.25 * sob
        x = W * bx + math.sin(t * 2 + fase) * W * 0.03
        r = H * br * (1 + 0.4 * sob)
        g = cairo.RadialGradient(x, y, 0, x, y, r)
        a = (1 - dissolve)
        g.add_color_stop_rgba(0, *st["tinta"], 0.95 * a)
        g.add_color_stop_rgba(0.6, *st["tinta"], 0.85 * a)
        g.add_color_stop_rgba(1, *st["tinta"], 0)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
    if abs(t - c) < 0.1:  # no corte, tela toda branca de vapor
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgb(*st["tinta"])
        ctx.fill()
    if e.get("texto"):
        a = min(ease((t - c * 0.6) / 0.2), 1 - dissolve)
        if a > 0:
            ctx.select_font_face("Source Serif 4", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(H * 0.11)
            ext = ctx.text_extents(e["texto"])
            ctx.move_to(W / 2 - ext.width / 2 - ext.x_bearing, H / 2 + ext.height / 2 - H * 0.04 * ease((t - c) / 0.6))
            ctx.set_source_rgba(*st["fundo"], a)
            ctx.show_text(e["texto"])


# ---------- rebobinar (VHS) ----------

def rebobinar(ctx, st, e, t, W, H, c):
    """Fita VHS rebobinando: linhas de varredura, faixa de rastreio, "◀◀ REW" e o relógio da fita correndo
    para trás ("de_hora" -> "para_hora", ex.: "20:41" -> "07:02"); no corte, tela azul de VHS."""
    dur = e["ate"] - e["de"]
    perto = 1 - min(1.0, abs(t - c) / max(0.15, max(c, dur - c)))
    if t <= c + 0.12 and t >= c - 0.12:
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgb(0.02, 0.08, 0.55)  # azul de VCR, só nos quadros do corte
        ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.25 * perto)  # linhas de varredura
    for y in range(0, H, 4):
        ctx.rectangle(0, y, W, 2)
    ctx.fill()
    rnd = __import__("random").Random(int(t * 30))
    for _ in range(3):  # faixas de rastreio que correm
        y = (t * 1.7 * H + rnd.uniform(0, H)) % H
        ctx.rectangle(0, y, W, H * rnd.uniform(0.01, 0.05))
        ctx.set_source_rgba(*st["tinta"], 0.35 * perto)
        ctx.fill()
    ctx.select_font_face("DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(H * 0.075)
    pisca = int(t * 4) % 2 == 0
    ctx.set_source_rgba(1, 1, 1, 0.95 * (1 if pisca else 0.6))
    ctx.move_to(W * 0.06, H * 0.14)
    ctx.show_text(e.get("rotulo", "<< REW"))
    def minutos(s):
        h, m = s.split(":")
        return int(h) * 60 + int(m)
    if e.get("de_hora"):  # só mostra o relógio da fita quando as horas são conhecidas
        a, b = minutos(e["de_hora"]), minutos(e.get("para_hora", "07:00"))
        m = a + (b - a) * ease(t / dur)
        ctx.move_to(W * 0.72, H * 0.9)
        ctx.show_text(f"{int(m) // 60:02d}:{int(m) % 60:02d}")
    ctx.set_font_size(H * 0.035)
    ctx.move_to(W * 0.06, H * 0.9)
    ctx.show_text("SP  " + e.get("texto", ""))


ESTILOS = {"roda": roda, "rota": rota, "relogio": relogio, "cortina": cortina, "flash": flash, "blocos": blocos,
           "tinta": tinta, "glitch": glitch, "papel": papel, "iris": iris, "persiana": persiana, "filme": filme,
           "celular": celular, "polaroid": polaroid, "cronometro": cronometro, "cupom": cupom, "anilhas": anilhas,
           "vapor": vapor, "rebobinar": rebobinar}


def desenhar(ctx, st, e, t, W, H):
    ESTILOS[e["estilo"]](ctx, st, e, t, W, H, e["corte"])


def tempos(e, corte_editado):
    """de/ate no vídeo editado em volta do corte."""
    antes, depois = DURACAO[e["estilo"]]
    antes, depois = e.get("antes", antes), e.get("depois", depois)
    return dict(e, de=corte_editado - antes, ate=corte_editado + depois, corte=antes)
