"""Mecanismos clássicos desenhados com cairo (formato "como funciona" em 2D): fechadura de pinos, catraca, cruz de
Malta (Geneva drive), escapamento de âncora e engrenagem planetária. Cada função recebe t (s desde o início da cena)
e calcula a cinemática de verdade (razões de dentes, ângulos de engate)."""
import math

from core import AREA, WHITE, round_rect, text_center
from physics import panel

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2
FUNDO = (0.05, 0.06, 0.10)
LATAO = (0.93, 0.74, 0.32)
ACO = (0.72, 0.76, 0.82)
AZUL = (0.36, 0.78, 0.98)
ROSA = (1.0, 0.36, 0.54)
VERDE = (0.30, 0.90, 0.50)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def engrenagem(ctx, x, y, r, dentes, ang, cor, furo=True):
    """Engrenagem de dentes trapezoidais; r = raio primitivo (dentes ficam metade para fora, metade para dentro)."""
    h = r * 2 * math.pi / dentes * 0.55
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    passo = 2 * math.pi / dentes
    for k in range(dentes):
        a = k * passo
        ctx.line_to((r - h / 2) * math.cos(a), (r - h / 2) * math.sin(a))
        ctx.line_to((r + h / 2) * math.cos(a + passo * 0.18), (r + h / 2) * math.sin(a + passo * 0.18))
        ctx.line_to((r + h / 2) * math.cos(a + passo * 0.42), (r + h / 2) * math.sin(a + passo * 0.42))
        ctx.line_to((r - h / 2) * math.cos(a + passo * 0.6), (r - h / 2) * math.sin(a + passo * 0.6))
    ctx.close_path()
    ctx.set_source_rgb(*cor)
    ctx.fill()
    if furo:
        ctx.arc(0, 0, r * 0.22, 0, 2 * math.pi)
        ctx.set_source_rgb(*FUNDO)
        ctx.fill()
        ctx.set_source_rgba(0, 0, 0, 0.18)
        for k in range(4):
            ctx.save()
            ctx.rotate(k * math.pi / 2)
            round_rect(ctx, r * 0.32, -r * 0.09, r * 0.4, r * 0.18, r * 0.05)
            ctx.restore()
        ctx.fill()
    ctx.restore()


# ---------------- #5 fechadura de pinos (pin tumbler) ----------------

PINOS_X = [330, 470, 610, 750]
PINO_L = [95, 60, 115, 75]        # comprimento dos pinos de baixo (latão): o "segredo" da chave
SHEAR = 830                       # linha de corte entre o cilindro e o corpo
FUNDO_CANAL = 975


def _topo_chave(x, desloc):
    """y do topo da lâmina da chave na posição x do mundo (a chave entra da esquerda; desloc = quanto falta)."""
    u = x + desloc                      # coordenada na chave, já na posição final
    ponta = 900
    if x > ponta - desloc or u < 190:
        return None
    vales = [(px, SHEAR + L) for px, L in zip(PINOS_X, PINO_L)]
    y = 865.0                           # cristas entre os vales
    for px, vy in vales:
        d = abs(u - px)
        if d < 45:
            y = max(y, vy - (vy - 865) * max(0.0, (d - 12) / 33))
    if u > ponta - 60:                  # ponta chanfrada
        y = max(y, 865 + (u - (ponta - 60)) * 1.4)
    return min(y, 970)


def fechadura(ctx, t, entra=(0.3, 2.6)):
    panel(ctx)
    k = ease((t - entra[0]) / (entra[1] - entra[0]))
    desloc = 760 * (1 - k)
    aberto = k >= 1.0
    gira = ease((t - entra[1] - 0.3) / 0.6)
    ctx.set_source_rgb(0.30, 0.33, 0.40)  # corpo
    round_rect(ctx, 170, 600, 740, 420, 30)
    ctx.fill()
    ctx.set_source_rgb(0.55, 0.48, 0.30) if not aberto else ctx.set_source_rgb(0.62, 0.55, 0.32)
    round_rect(ctx, 190, SHEAR, 700, 170, 18)  # cilindro (gira quando todos os pinos alinham)
    ctx.fill()
    ctx.set_source_rgb(*FUNDO)  # canal da chave
    ctx.rectangle(190, 900, 700, 75)
    ctx.fill()
    for px, L in zip(PINOS_X, PINO_L):
        ctx.set_source_rgb(*FUNDO)
        ctx.rectangle(px - 26, 625, 52, FUNDO_CANAL - 625 - 70)
        ctx.fill()
        topo = _topo_chave(px, desloc)
        base = topo if topo is not None else FUNDO_CANAL - 25
        ctx.set_source_rgb(*LATAO)  # pino de baixo (ponta arredondada encosta na chave)
        round_rect(ctx, px - 22, base - L, 44, L, 12)
        ctx.fill()
        ctx.set_source_rgb(*ACO)  # pino de cima
        round_rect(ctx, px - 22, base - L - 100, 44, 98, 8)
        ctx.fill()
        ctx.set_source_rgb(0.85, 0.85, 0.9)  # mola
        ctx.set_line_width(5)
        topo_mola = base - L - 100
        n = 7
        ctx.move_to(px, 630)
        for i in range(1, n + 1):
            yy = 630 + (topo_mola - 630) * i / n
            ctx.line_to(px + (18 if i % 2 else -18), yy)
        ctx.stroke()
    # chave
    ctx.set_source_rgb(0.80, 0.82, 0.86)
    xs = list(range(190, 901, 6))
    pts = [(x, _topo_chave(x, desloc)) for x in xs]
    pts = [(x, y) for x, y in pts if y is not None]
    if pts:
        ctx.move_to(pts[0][0], 975)
        for x, y in pts:
            ctx.line_to(x, y)
        ctx.line_to(pts[-1][0], 975)
        ctx.close_path()
        ctx.fill()
    cabo_x = 190 - desloc
    ctx.set_source_rgb(0.80, 0.82, 0.86)
    ctx.arc(cabo_x - 70, 930, 80, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(*FUNDO)
    ctx.arc(cabo_x - 90, 930, 24, 0, 2 * math.pi)
    ctx.fill()
    linha = VERDE if aberto else ROSA
    ctx.set_source_rgba(*linha, 0.9)
    ctx.set_line_width(5)
    ctx.set_dash([16, 10])
    ctx.move_to(170, SHEAR)
    ctx.line_to(910, SHEAR)
    ctx.stroke()
    ctx.set_dash([])
    text_center(ctx, "SHEAR LINE", 540, SHEAR - 14 - 200, 30, linha, "ExtraBold", alpha=0.0)
    if aberto:
        text_center(ctx, "UNLOCKED", 540, 1130, 64, VERDE, "ExtraBold", alpha=gira)
        ctx.save()  # seta girando
        ctx.translate(540, 1210)
        ctx.new_path()
        ctx.set_source_rgba(*VERDE, gira)
        ctx.set_line_width(10)
        ctx.arc(0, 0, 34, -math.pi * 0.9, -math.pi * 0.9 + math.pi * 1.5 * gira)
        ctx.stroke()
        ctx.restore()


# ---------------- #4 catraca (ratchet) ----------------

def _raio_catraca(phi, r, h, n):
    p = 2 * math.pi / n
    f = (phi % p) / p
    return r + h * (1 - f)


def catraca(ctx, t, frente=(0.0, 2.6), volta=(2.6, 4.2)):
    panel(ctx)
    n, r, h = 16, 230, 46
    cx, cy = CX - 40, CY + 40
    if t < frente[1]:
        th = 1.1 * (t - frente[0])
        trava = 0.0
    else:  # tenta voltar e trava no dente: só balança um pouco
        th = 1.1 * (frente[1] - frente[0])
        lt = t - volta[0]
        th -= 0.06 * abs(math.sin(lt * 9)) * math.exp(-lt * 0.8)
        trava = 1.0
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(th)
    m = 240
    for i in range(m + 1):
        phi = 2 * math.pi * i / m
        rr = _raio_catraca(phi, r, h, n)
        ctx.line_to(rr * math.cos(phi), rr * math.sin(phi))
    ctx.close_path()
    ctx.set_source_rgb(*AZUL)
    ctx.fill()
    ctx.arc(0, 0, 50, 0, 2 * math.pi)
    ctx.set_source_rgb(*FUNDO)
    ctx.fill()
    ctx.restore()
    phi = -math.pi / 2 - th  # ângulo do dente sob a lingueta, nas coordenadas da roda
    rr = _raio_catraca(phi, r, h, n)
    tip = (cx, cy - rr)
    piv = (cx + 250, cy - r - 120)
    ctx.set_source_rgb(*ROSA)  # lingueta
    ctx.set_line_width(26)
    ctx.set_line_cap(1)
    ctx.move_to(*piv)
    ctx.line_to(*tip)
    ctx.stroke()
    ctx.arc(*piv, 26, 0, 2 * math.pi)
    ctx.set_source_rgb(0.9, 0.9, 0.95)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.85, 0.9)  # mola que empurra a lingueta para baixo
    ctx.set_line_width(5)
    sx, sy = piv[0] + 40, piv[1] - 140
    for i in range(9):
        ctx.line_to(sx + (14 if i % 2 else -14), sy + i * 14)
    ctx.line_to(piv[0] + 10, piv[1] - 10)
    ctx.stroke()
    cor = VERDE if not trava else ROSA
    texto = "SPINS FREE" if not trava else "LOCKED"
    text_center(ctx, texto, CX, Y1 - 40, 60, cor, "ExtraBold")
    ctx.save()  # seta do sentido
    ctx.translate(cx, cy)
    ctx.new_path()
    ctx.set_source_rgba(*cor, 0.9)
    ctx.set_line_width(10)
    if not trava:
        ctx.arc(0, 0, r + 90, -0.2, 0.7)
    else:
        ctx.arc_negative(0, 0, r + 90, 0.7, 0.3)
    ctx.stroke()
    ctx.restore()


# ---------------- #3 cruz de Malta (Geneva drive) ----------------

def geneva(ctx, t, w=2.0):
    panel(ctx)
    a = 165.0
    d = a * math.sqrt(2)
    cd = (CX - 150, CY + 20)
    cs = (cd[0] + d, cd[1])
    alpha = w * t - math.pi / 4 - 0.6  # ângulo do pino (0 = apontando para o centro da estrela)
    ciclo = math.floor((alpha + math.pi / 4) / (2 * math.pi))
    local = alpha - ciclo * 2 * math.pi
    P = (cd[0] + a * math.cos(local), cd[1] + a * math.sin(local))
    entrada = math.pi + math.pi / 4  # direção da ranhura (vista do centro da estrela) quando o pino entra
    if local < math.pi / 4:
        psi = math.atan2(P[1] - cs[1], P[0] - cs[0])
        giro = (psi - entrada + math.pi) % (2 * math.pi) - math.pi
        beta = giro + ciclo * (-math.pi / 2)
        mexendo = True
    else:
        beta = (ciclo + 1) * (-math.pi / 2)
        mexendo = False
    R = d * math.cos(math.pi / 4) * 1.12
    ctx.save()
    ctx.translate(*cs)
    ctx.rotate(beta)
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    ctx.set_source_rgb(*LATAO)
    ctx.fill()
    ctx.set_source_rgb(*FUNDO)
    for k in range(4):  # ranhuras e as concavidades de travamento
        ang = entrada + k * math.pi / 2
        ctx.save()
        ctx.rotate(ang)
        ctx.rectangle(d - a - 30, -21, R, 42)
        ctx.fill()
        ctx.restore()
        ang2 = ang + math.pi / 4
        ctx.new_sub_path()
        ctx.arc(d * math.cos(ang2), d * math.sin(ang2), a * 0.74, 0, 2 * math.pi)
        ctx.fill()
    ctx.arc(0, 0, 28, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    ctx.save()  # roda motora: disco de trava com recorte + braço com o pino
    ctx.translate(*cd)
    ctx.arc(0, 0, a * 0.72, 0, 2 * math.pi)
    ctx.set_source_rgb(*AZUL)
    ctx.fill()
    ctx.set_source_rgb(*FUNDO)
    ctx.arc(a * 0.95 * math.cos(local), a * 0.95 * math.sin(local), a * 0.55, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(*AZUL)
    ctx.set_line_width(30)
    ctx.set_line_cap(1)
    ctx.move_to(0, 0)
    ctx.line_to(a * math.cos(local), a * math.sin(local))
    ctx.stroke()
    ctx.arc(a * math.cos(local), a * math.sin(local), 22, 0, 2 * math.pi)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.arc(0, 0, 20, 0, 2 * math.pi)
    ctx.set_source_rgb(*FUNDO)
    ctx.fill()
    ctx.restore()
    text_center(ctx, "MOVE" if mexendo else "STOP", CX, Y1 - 50, 64, VERDE if mexendo else ROSA, "ExtraBold")
    text_center(ctx, f"STEP {ciclo + 1 + (0 if mexendo else 1)}", CX, Y0 + 70, 40, WHITE, "Bold")


# ---------------- #2 escapamento de âncora (relógio de pêndulo) ----------------

def escapamento(ctx, t, periodo=1.4):
    panel(ctx)
    n = 30
    piv = (CX, Y0 + 90)
    wc = (CX, Y0 + 400)
    piv = (CX, Y0 + 70)
    rw = 170
    amp = 0.22
    th = amp * math.sin(2 * math.pi * t / periodo)
    meio = math.floor(t / (periodo / 2))
    frac = (t - meio * periodo / 2) / 0.07
    passo = 2 * math.pi / n / 2  # meio dente a cada meia oscilação (um dente por oscilação completa)
    ang_roda = (meio + ease(frac)) * passo
    # roda de escape: dentes inclinados
    ctx.save()
    ctx.translate(*wc)
    ctx.rotate(ang_roda)
    for k in range(n):
        a = k * 2 * math.pi / n
        ctx.line_to(rw * 0.86 * math.cos(a), rw * 0.86 * math.sin(a))
        ctx.line_to(rw * math.cos(a + 0.05), rw * math.sin(a + 0.05))
        ctx.line_to(rw * 0.86 * math.cos(a + 2 * math.pi / n), rw * 0.86 * math.sin(a + 2 * math.pi / n))
    ctx.close_path()
    ctx.set_source_rgb(*LATAO)
    ctx.fill()
    ctx.arc(0, 0, 40, 0, 2 * math.pi)
    ctx.set_source_rgb(*FUNDO)
    ctx.fill()
    ctx.restore()
    # pêndulo (atrás) e âncora (presa no mesmo eixo)
    L = 650
    bob = (piv[0] + L * math.sin(th), piv[1] + L * math.cos(th))
    ctx.set_source_rgba(*ACO, 0.9)
    ctx.set_line_width(14)
    ctx.move_to(*piv)
    ctx.line_to(*bob)
    ctx.stroke()
    ctx.arc(*bob, 70, 0, 2 * math.pi)
    ctx.set_source_rgb(*LATAO)
    ctx.fill()
    ctx.save()
    ctx.translate(*piv)
    ctx.rotate(-th)
    ctx.set_source_rgb(*ROSA)
    ctx.set_line_width(24)
    ctx.set_line_cap(1)
    for s in (-1, 1):
        ctx.move_to(0, 0)
        ctx.line_to(s * 150, 160)
        ctx.line_to(s * 108, 222)
    ctx.stroke()
    ctx.arc(0, 0, 26, 0, 2 * math.pi)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.restore()
    if frac < 1.6:
        text_center(ctx, "TICK" if meio % 2 == 0 else "TOCK", CX + 250, Y0 + 140, 54, WHITE, "ExtraBold",
                    alpha=max(0.0, 1 - frac / 1.6))


# ---------------- #1 engrenagem planetária ----------------

SOL, PLANETA, ANEL = 12, 12, 36   # ANEL = SOL + 2 PLANETA


def planetaria(ctx, t, w=1.6, marca=True):
    panel(ctx)
    m = 6.2                         # raio primitivo por dente
    rs, rp, ra = SOL * m, PLANETA * m, ANEL * m
    c = (CX, CY + 10)
    th_s = w * t
    th_c = th_s * SOL / (SOL + ANEL)  # anel parado: o suporte gira 1/4 da velocidade do sol
    # anel com dentes para dentro
    ctx.save()
    ctx.translate(*c)
    ctx.arc(0, 0, ra + 70, 0, 2 * math.pi)
    ctx.set_source_rgb(*ACO)
    ctx.fill()
    h = ra * 2 * math.pi / ANEL * 0.55
    passo = 2 * math.pi / ANEL
    for k in range(ANEL):
        a = k * passo + passo / 2
        ctx.line_to((ra + h / 2) * math.cos(a), (ra + h / 2) * math.sin(a))
        ctx.line_to((ra - h / 2) * math.cos(a + passo * 0.18), (ra - h / 2) * math.sin(a + passo * 0.18))
        ctx.line_to((ra - h / 2) * math.cos(a + passo * 0.42), (ra - h / 2) * math.sin(a + passo * 0.42))
        ctx.line_to((ra + h / 2) * math.cos(a + passo * 0.6), (ra + h / 2) * math.sin(a + passo * 0.6))
    ctx.close_path()
    ctx.set_source_rgb(*FUNDO)
    ctx.fill()
    ctx.restore()
    # suporte (braço que liga os planetas = a saída)
    ctx.save()
    ctx.translate(*c)
    ctx.rotate(th_c)
    ctx.set_source_rgba(*VERDE, 0.55)
    ctx.set_line_width(34)
    ctx.set_line_cap(1)
    for k in range(3):
        a = k * 2 * math.pi / 3
        ctx.move_to(0, 0)
        ctx.line_to((rs + rp) * math.cos(a), (rs + rp) * math.sin(a))
    ctx.stroke()
    ctx.restore()
    for k in range(3):
        a = th_c + k * 2 * math.pi / 3
        px, py = c[0] + (rs + rp) * math.cos(a), c[1] + (rs + rp) * math.sin(a)
        th_p = th_c - (th_s - th_c) * SOL / PLANETA   # rola por dentro do anel parado
        engrenagem(ctx, px, py, rp, PLANETA, th_p + a * (1 + SOL / PLANETA) + math.pi / PLANETA * 0.5 - 0.31,
                   AZUL)
        ctx.arc(px, py, 16, 0, 2 * math.pi)
        ctx.set_source_rgb(*VERDE)
        ctx.fill()
    engrenagem(ctx, c[0], c[1], rs, SOL, th_s, LATAO)
    if marca:  # marcas para ver as voltas: sol (entrada) e suporte (saída)
        for ang, rr, cor in ((th_s, rs * 0.55, ROSA), (th_c, (rs + rp) * 0.5, VERDE)):
            ctx.arc(c[0] + rr * math.cos(ang), c[1] + rr * math.sin(ang), 12, 0, 2 * math.pi)
            ctx.set_source_rgb(*cor)
            ctx.fill()
        voltas_s = th_s / (2 * math.pi)
        text_center(ctx, f"IN {voltas_s:.1f} turns", CX - 220, Y1 - 30, 40, ROSA, "ExtraBold")
        text_center(ctx, f"OUT {voltas_s * SOL / (SOL + ANEL):.1f} turns", CX + 220, Y1 - 30, 40, VERDE, "ExtraBold")
