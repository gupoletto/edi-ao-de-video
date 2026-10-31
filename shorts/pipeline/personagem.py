"""Quark, o mascote do Fun Stuff: desenhado 100% por código (cairo), animado por parâmetros.

Um "feijão" amarelo com óculos de laboratório na testa, braços e pernas de borracha (estilo cartoon clássico), luvas
brancas e tênis rosa. A boca acompanha a voz (`boca_da_voz`).

    q = Pose(expr="surpreso", olhar=(0.6, -0.2), braco_d=2.4, andar=t * 2)
    quark(ctx, x, y_chao, altura_px, q, t)

Ângulos dos braços em radianos a partir de "pendurado para baixo"; positivo levanta o braço para fora do corpo.
"""
import math
from dataclasses import dataclass, field

import numpy as np

AMARELO = (1.0, 0.80, 0.24)
AMARELO_SOMBRA = (0.93, 0.62, 0.16)
AMARELO_LUZ = (1.0, 0.92, 0.55)
TINTA = (0.10, 0.09, 0.13)
LUVA = (0.98, 0.97, 0.95)
TENIS = (1.0, 0.36, 0.54)
MEMBRO = (0.95, 0.60, 0.16)  # braços e pernas: laranja com contorno escuro, para aparecer no fundo escuro
LENTE = (0.36, 0.78, 0.98)
SR = 24000


@dataclass
class Pose:
    expr: str = "neutro"          # neutro feliz rindo surpreso medo pensando bravo tonto determinado
    olhar: tuple = (0.0, 0.0)     # -1..1 em x e y
    piscar: float = None          # 0 aberto .. 1 fechado; None = piscada automática
    boca: float = 0.0             # abertura extra da fala, 0..1
    braco_e: float = 0.25         # ângulo do braço esquerdo da tela
    braco_d: float = 0.25
    cotovelo_e: float = 0.0       # dobra (curva da mangueira), -1..1
    cotovelo_d: float = 0.0
    andar: float = None           # fase da caminhada/corrida (ciclos); None = parado
    corrida: bool = False         # passos mais largos e corpo inclinado
    pulo: float = 0.0             # 0..1 encolhe as pernas (no ar)
    squash: float = 1.0           # >1 estica, <1 achata (volume preservado)
    inclina: float = 0.0          # inclinação do corpo (rad)
    capacete: bool = False        # capacete de astronauta (bolha)
    suor: bool = False
    extra: dict = field(default_factory=dict)


def piscada_auto(t, seed=0):
    """Pisca a cada ~3 s (com variação determinística); dura 0,14 s."""
    periodo = 3.1 + 0.6 * math.sin(seed * 1.7)
    fase = (t + seed * 0.37) % periodo
    return max(0.0, 1 - abs(fase - 0.07) / 0.07) if fase < 0.14 else 0.0


def boca_da_voz(seg, t, ganho=6.0):
    """Abertura da boca 0..1 a partir da voz do segmento (RMS em janela de 60 ms)."""
    for ini, a in getattr(seg, "audio", ()):
        i = int((t - ini) * SR)
        if 0 <= i < len(a):
            j0, j1 = max(0, i - 720), min(len(a), i + 720)
            rms = float(np.sqrt(np.mean(a[j0:j1] ** 2))) if j1 > j0 else 0.0
            return min(1.0, rms * ganho)
    return 0.0


def _corpo(ctx, w, h):
    """Feijão: superelipse um pouco mais larga embaixo. Origem no centro do corpo."""
    n = 2.6
    ctx.new_path()
    for k in range(73):
        a = 2 * math.pi * k / 72
        c, s = math.cos(a), math.sin(a)
        x = (w / 2) * math.copysign(abs(c) ** (2 / n), c)
        y = (h / 2) * math.copysign(abs(s) ** (2 / n), s)
        x *= 1 + 0.08 * (y / (h / 2))  # base mais larga
        (ctx.line_to if k else ctx.move_to)(x, y)
    ctx.close_path()


def _mangueira(ctx, x0, y0, x1, y1, dobra, lw):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    d = math.hypot(nx, ny) or 1
    cx, cy = mx + nx / d * dobra, my + ny / d * dobra
    ctx.move_to(x0, y0)
    ctx.curve_to(x0 + (cx - x0) * 0.7, y0 + (cy - y0) * 0.7, x1 + (cx - x1) * 0.7, y1 + (cy - y1) * 0.7, x1, y1)
    ctx.set_line_cap(1)
    caminho = ctx.copy_path()
    ctx.set_source_rgb(*TINTA)
    ctx.set_line_width(lw * 1.6)
    ctx.stroke()
    ctx.append_path(caminho)
    ctx.set_source_rgb(*MEMBRO)
    ctx.set_line_width(lw * 0.9)
    ctx.stroke()


def _luva(ctx, x, y, r, ang, lw):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.arc(r * 0.75, -r * 0.55, r * 0.42, 0, 2 * math.pi)  # polegar
    ctx.set_source_rgb(*LUVA)
    ctx.fill_preserve()
    ctx.set_source_rgb(*TINTA)
    ctx.set_line_width(lw * 0.5)
    ctx.stroke()
    ctx.restore()


def _tenis(ctx, x, y, r, lado, lw):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(lado, 1)
    ctx.move_to(-r * 0.7, 0)
    ctx.curve_to(-r * 0.8, -r * 0.9, r * 0.3, -r * 1.0, r * 0.6, -r * 0.45)
    ctx.curve_to(r * 1.2, -r * 0.35, r * 1.3, 0, r * 1.1, 0)
    ctx.close_path()
    ctx.set_source_rgb(*TENIS)
    ctx.fill_preserve()
    ctx.set_source_rgb(*TINTA)
    ctx.set_line_width(lw * 0.55)
    ctx.stroke()
    ctx.rectangle(-r * 0.75, -r * 0.16, r * 1.9, r * 0.16)  # sola
    ctx.set_source_rgb(*LUVA)
    ctx.fill()
    ctx.restore()


def _olho(ctx, x, y, rx, ry, olhar, fecha, expr, lado, lw):
    ctx.save()
    ctx.translate(x, y)
    ctx.save()
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    tam = 0.42 if expr not in ("medo", "surpreso") else 0.3  # pupila encolhe no susto
    px, py = olhar[0] * rx * 0.45, olhar[1] * ry * 0.4
    if expr == "tonto":  # espiral
        ctx.new_path()
        for k in range(60):
            a = k * 0.32
            r = rx * 0.08 + rx * 0.012 * k
            (ctx.line_to if k else ctx.move_to)(r * math.cos(a * lado), r * math.sin(a * lado))
        ctx.set_source_rgb(*TINTA)
        ctx.set_line_width(lw * 0.35)
        ctx.stroke()
    else:
        ctx.arc(px, py, rx * tam * 1.25, 0, 2 * math.pi)
        ctx.set_source_rgb(*TINTA)
        ctx.fill()
        ctx.arc(px - rx * 0.12, py - ry * 0.14, rx * 0.11, 0, 2 * math.pi)  # brilho
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
    # pálpebra (cor do corpo) descendo; bravo/determinado inclina para dentro, medo/pensando para fora
    inc = -{"bravo": 0.35, "determinado": 0.25, "medo": -0.3, "pensando": -0.15}.get(expr, 0.0) * lado
    base = {"feliz": 0.12, "rindo": 1.0, "pensando": 0.3, "determinado": 0.32, "bravo": 0.4}.get(expr, 0.0)
    f = min(1.0, base + fecha * (1 - base))
    if f > 0.01:
        ctx.new_path()
        y_lid = -ry + 2 * ry * f
        ctx.move_to(-rx * 1.2, -ry * 1.3)
        ctx.line_to(rx * 1.2, -ry * 1.3)
        ctx.line_to(rx * 1.2, y_lid + inc * ry)
        ctx.line_to(-rx * 1.2, y_lid - inc * ry)
        ctx.close_path()
        ctx.set_source_rgb(*AMARELO)
        ctx.fill_preserve()
        ctx.set_source_rgb(*TINTA)
        ctx.set_line_width(lw * 0.4)
        ctx.stroke()
    ctx.restore()
    ctx.save()
    if expr == "rindo":  # olhos fechados em arco "^"
        ctx.new_path()
        ctx.move_to(-rx * 0.8, ry * 0.35)
        ctx.curve_to(-rx * 0.4, -ry * 0.4, rx * 0.4, -ry * 0.4, rx * 0.8, ry * 0.35)
        ctx.set_source_rgb(*TINTA)
        ctx.set_line_width(lw * 0.45)
        ctx.stroke()
    ctx.restore()
    if expr != "rindo":
        ctx.save()
        ctx.scale(rx, ry)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(*TINTA)
        ctx.set_line_width(lw * 0.5)
        ctx.stroke()
    ctx.restore()


def _sobrancelha(ctx, x, y, w, expr, lado, lw, t):
    ang, dy = {"bravo": (0.45, 0.1), "determinado": (0.3, 0.05), "medo": (-0.45, -0.2), "surpreso": (-0.1, -0.35),
               "pensando": (-0.25 if lado < 0 else 0.15, -0.15 if lado < 0 else 0.05), "tonto": (-0.2, -0.1),
               "feliz": (-0.08, -0.12), "rindo": (-0.1, -0.15)}.get(expr, (0.0, -0.05))
    ctx.save()
    ctx.translate(x, y + dy * w)
    ctx.rotate(ang * lado)
    ctx.move_to(-w / 2, 0)
    ctx.curve_to(-w / 4, -w * 0.18, w / 4, -w * 0.18, w / 2, 0)
    ctx.set_source_rgb(*TINTA)
    ctx.set_line_width(lw * 0.75)
    ctx.set_line_cap(1)
    ctx.stroke()
    ctx.restore()


def _boca(ctx, x, y, w, expr, fala, lw):
    ctx.save()
    ctx.translate(x, y)
    abre = {"surpreso": 0.55, "medo": 0.45, "rindo": 0.5}.get(expr, 0.0)
    abre = max(abre, fala * 0.6)
    ctx.set_line_cap(1)
    ctx.set_line_join(1)
    if expr == "medo" and fala < 0.2:  # boca ondulada
        ctx.move_to(-w / 2, 0)
        for k in range(1, 9):
            ctx.line_to(-w / 2 + w * k / 8, (w * 0.08) * (1 if k % 2 else -1))
        ctx.set_source_rgb(*TINTA)
        ctx.set_line_width(lw * 0.5)
        ctx.stroke()
    elif abre > 0.05:
        sorri = expr in ("feliz", "rindo")
        hw = w * (0.5 if sorri else 0.32 + 0.1 * fala)
        h = w * 0.7 * abre
        ctx.move_to(-hw, 0)
        if sorri:
            ctx.curve_to(-hw * 0.5, -w * 0.05, hw * 0.5, -w * 0.05, hw, 0)
            ctx.curve_to(hw * 0.7, h * 1.2, -hw * 0.7, h * 1.2, -hw, 0)
        else:
            ctx.curve_to(-hw, -h * 0.7, hw, -h * 0.7, hw, 0)
            ctx.curve_to(hw, h, -hw, h, -hw, 0)
        ctx.close_path()
        ctx.set_source_rgb(0.35, 0.08, 0.12)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip_preserve()
        ctx.new_path()
        ctx.arc(0, h * 0.9, hw * 0.55, 0, 2 * math.pi)  # língua
        ctx.set_source_rgb(1.0, 0.45, 0.5)
        ctx.fill()
        ctx.restore()
        ctx.set_source_rgb(*TINTA)
        ctx.set_line_width(lw * 0.5)
        ctx.stroke()
    else:
        curva = {"feliz": 0.22, "determinado": 0.0, "pensando": -0.05, "bravo": -0.16, "tonto": 0.05,
                 "neutro": 0.1}.get(expr, 0.08)
        hw = w * (0.45 if expr == "feliz" else 0.32)
        if expr == "pensando":
            ctx.move_to(-hw, w * 0.04)
            ctx.line_to(hw, -w * 0.04)
        else:
            ctx.move_to(-hw, 0)
            ctx.curve_to(-hw * 0.4, w * curva, hw * 0.4, w * curva, hw, 0)
        ctx.set_source_rgb(*TINTA)
        ctx.set_line_width(lw * 0.55)
        ctx.stroke()
    ctx.restore()


def _oculos(ctx, w, h, y, lw):
    """Óculos de laboratório na testa: faixa (recortada no corpo) + duas lentes azuis."""
    ctx.save()
    _corpo(ctx, w, h)
    ctx.clip()
    ctx.rectangle(-w * 0.6, y - w * 0.05, w * 1.2, w * 0.1)
    ctx.set_source_rgb(0.25, 0.27, 0.33)
    ctx.fill()
    ctx.restore()
    _corpo(ctx, w, h)
    ctx.set_source_rgb(*TINTA)
    ctx.set_line_width(lw)
    ctx.stroke()
    for sx in (-1, 1):
        cx = sx * w * 0.17
        ctx.arc(cx, y, w * 0.13, 0, 2 * math.pi)
        ctx.set_source_rgb(0.25, 0.27, 0.33)
        ctx.fill()
        ctx.arc(cx, y, w * 0.095, 0, 2 * math.pi)
        g_ = LENTE
        ctx.set_source_rgb(*g_)
        ctx.fill()
        ctx.arc(cx - w * 0.03, y - w * 0.03, w * 0.03, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.fill()


def quark(ctx, x, y, h, p=None, t=0.0, seed=0):
    """Desenha o Quark com os pés em (x, y) e altura total h (px)."""
    import cairo
    p = p or Pose()
    lw = h * 0.032
    perna = h * 0.2 * (1 - 0.45 * p.pulo)
    hb = h * 0.74
    wb = hb * 0.86
    sy = p.squash
    sx = 1 / math.sqrt(sy)
    respira = 1 + 0.012 * math.sin(t * 2.4 + seed)
    passo = 0.0
    if p.andar is not None:
        passo = math.sin(2 * math.pi * p.andar)
    quica = abs(math.sin(2 * math.pi * p.andar)) * h * (0.045 if p.corrida else 0.025) if p.andar is not None else 0
    inclina = p.inclina + (0.18 if p.corrida else 0.0)
    cy = y - perna - hb / 2 * sy - quica
    # pernas e tênis (atrás do corpo)
    for lado in (-1, 1):
        qx = x + lado * wb * 0.2
        fase = passo * lado
        amp = (0.55 if p.corrida else 0.32) * h * 0.25
        px_ = qx + fase * amp
        py_ = y - max(0.0, -fase if p.andar is not None else 0) * h * 0.06 - (h * 0.1 * p.pulo)
        _mangueira(ctx, qx, cy + hb * 0.38 * sy, px_, py_ - h * 0.03, lado * h * 0.02, lw * 1.25)
        _tenis(ctx, px_, py_, h * 0.075, 1 if lado > 0 else -1, lw)
    ctx.save()
    ctx.translate(x, cy + hb / 2 * sy)
    ctx.rotate(inclina)
    ctx.translate(0, -hb / 2 * sy)
    ctx.scale(sx * respira, sy / respira)
    # braços atrás? não: desenhados depois do corpo para ficarem visíveis
    _corpo(ctx, wb, hb)
    g = cairo.LinearGradient(-wb / 2, 0, wb / 2, 0)
    g.add_color_stop_rgb(0, *AMARELO_LUZ)
    g.add_color_stop_rgb(0.45, *AMARELO)
    g.add_color_stop_rgb(1, *AMARELO_SOMBRA)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*TINTA)
    ctx.set_line_width(lw)
    ctx.stroke()
    ctx.save()  # barriga clara
    ctx.translate(0, hb * 0.22)
    ctx.scale(wb * 0.3, hb * 0.18)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(*AMARELO_LUZ, 0.55)
    ctx.fill()
    # rosto
    fecha = p.piscar if p.piscar is not None else piscada_auto(t, seed)
    olho_y = -hb * 0.13
    for lado in (-1, 1):
        _olho(ctx, lado * wb * 0.17, olho_y, wb * 0.135, hb * 0.135, p.olhar, fecha, p.expr, lado, lw)
        _sobrancelha(ctx, lado * wb * 0.17, olho_y - hb * 0.17, wb * 0.17, p.expr, lado, lw, t)
    _boca(ctx, p.olhar[0] * wb * 0.03, hb * 0.08, wb * 0.26, p.expr, p.boca, lw)
    if p.expr in ("feliz", "rindo"):  # bochechas
        for lado in (-1, 1):
            ctx.arc(lado * wb * 0.33, hb * 0.04, wb * 0.06, 0, 2 * math.pi)
            ctx.set_source_rgba(1.0, 0.45, 0.45, 0.45)
            ctx.fill()
    _oculos(ctx, wb, hb, -hb * 0.38, lw)
    if p.suor:
        for k, (dx, dy) in enumerate(((0.42, -0.25), (0.47, -0.08))):
            fx, fy = wb * dx, hb * dy + (t * 60 + k * 20) % 25
            ctx.move_to(fx, fy - wb * 0.06)
            ctx.curve_to(fx + wb * 0.04, fy, fx + wb * 0.03, fy + wb * 0.04, fx, fy + wb * 0.04)
            ctx.curve_to(fx - wb * 0.03, fy + wb * 0.04, fx - wb * 0.04, fy, fx, fy - wb * 0.06)
            ctx.set_source_rgb(*LENTE)
            ctx.fill()
    # braços
    for lado, ang, dobra in ((-1, p.braco_e, p.cotovelo_e), (1, p.braco_d, p.cotovelo_d)):
        ox, oy = lado * wb * 0.44, hb * 0.08
        comp = h * 0.27
        ang_ = ang if p.andar is None else ang + 0.5 * math.sin(2 * math.pi * p.andar) * lado * (1.6 if p.corrida else 1)
        hx = ox + lado * math.sin(ang_) * comp
        hy = oy + math.cos(ang_) * comp
        _mangueira(ctx, ox, oy, hx, hy, (dobra * comp * 0.35 - comp * 0.08) * lado, lw * 1.15)
        _luva(ctx, hx, hy, h * 0.045, ang_ * lado + (math.pi / 2 if lado > 0 else -math.pi / 2), lw)
    if p.capacete:
        r = hb * 0.66
        ctx.arc(0, hb * 0.02, r, 0, 2 * math.pi)
        ctx.set_source_rgba(0.75, 0.9, 1.0, 0.16)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.set_line_width(lw * 0.8)
        ctx.stroke()
        ctx.arc(0, hb * 0.02, r * 0.82, math.radians(200), math.radians(245))
        ctx.set_source_rgba(1, 1, 1, 0.75)
        ctx.set_line_width(lw * 1.2)
        ctx.stroke()
    ctx.restore()


# ---------- assinatura do canal: o Quark faz a pergunta final de qualquer formato ----------

def seg_pergunta(fala, titulo, fundo=None, expr="feliz"):
    """Último segmento de qualquer Short: o Quark aparece, acena e faz a pergunta (comentários + marca do canal).

        SEGMENTS.append(seg_pergunta("Which one was your number one? Comment below.", "WHICH ONE WAS YOUR #1?",
                                     fundo=lambda ctx, t, s: sa.gears(ctx, t + 4)))
    `fundo(ctx, t, s)` redesenha a cena do vídeo atrás dele (opcional), escurecida para o Quark destacar; t é o tempo
    local do segmento (no 3D use `FILME.quadro(ctx, s.t0 + t)` para a cena seguir rodando).
    """
    from core import AREA, Seg

    def draw(ctx, t, s):
        if fundo:
            ctx.save()
            fundo(ctx, t, s)
            ctx.restore()
            ctx.set_source_rgba(0.02, 0.03, 0.06, 0.55)
            ctx.paint()
        entra = min(1.0, t / 0.45)
        y = AREA[3] - 40 + (1 - entra) ** 2 * 500  # sobe de baixo com um quique
        p = Pose(expr=expr, boca=boca_da_voz(s, t), braco_e=0.3 + 2.3 * min(1.0, max(0.0, (t - 0.3) / 0.3)),
                 braco_d=0.35, olhar=(0.25 * math.sin(t * 2.2), -0.25),
                 squash=1 + 0.1 * math.sin(min(t, 1.2) * 12) * max(0.0, 1 - t / 1.2))
        quark(ctx, (AREA[0] + AREA[2]) / 2, y, 560, p, t)
    return Seg([fala], draw, {"title": titulo}, tail=0.8)
