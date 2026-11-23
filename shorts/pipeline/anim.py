"""Biblioteca de animação "caprichada" para os episódios 2D (desde 23/11/2026, pedido do usuário: qualidade das
animações e gatilhos de atenção).

Volume e acabamento: sombra_chao, brilho, esfera, cilindro, bloco_3d, fundo_vivo (fundo com bokeh e vinheta).
Partículas: faiscas, estouro (explosão de linhas de impacto), confete, fumaca, bolhas.
Gatilhos de atenção: anel_destaque e seta (apontam o detalhe que a voz cita), contador (número correndo com tique),
texto_pop (palavras gigantes entrando uma a uma com mola), tremor (sacode a tela num impacto).
Todos recebem `t` em segundos desde que o efeito começou (t < 0 = ainda não apareceu) e tocam o som certo sozinhos
via core.evento_som.
"""
import math

import cairo

import core
from core import W, H, mola, text_center


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _rnd(i, s=0.0):
    v = math.sin(i * 12.9898 + s * 78.233) * 43758.5453
    return v - math.floor(v)


# ---------- volume e acabamento ----------

def sombra_chao(ctx, x, y, w, alpha=0.35):
    """Sombra elíptica suave no chão, sob um objeto centrado em x com base em y."""
    g = cairo.RadialGradient(x, y, 0, x, y, w / 2)
    g.add_color_stop_rgba(0, 0, 0, 0, alpha)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, 0.22)
    ctx.translate(-x, -y)
    ctx.new_path()
    ctx.arc(x, y, w / 2, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.restore()


def brilho(ctx, x, y, r, cor, alpha=0.6):
    """Halo de luz (glow) radial."""
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *cor, alpha)
    g.add_color_stop_rgba(0.4, *cor, alpha * 0.35)
    g.add_color_stop_rgba(1, *cor, 0)
    ctx.new_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()


def _clarear(c, k):
    return tuple(min(1.0, v + (1 - v) * k) for v in c)


def _escurecer(c, k):
    return tuple(v * (1 - k) for v in c)


def esfera(ctx, x, y, r, cor, alpha=1.0):
    """Esfera com luz de cima à esquerda, sombra própria e reflexo."""
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.4, r * 0.05, x, y, r * 1.05)
    g.add_color_stop_rgba(0, *_clarear(cor, 0.55), alpha)
    g.add_color_stop_rgba(0.55, *cor, alpha)
    g.add_color_stop_rgba(1, *_escurecer(cor, 0.45), alpha)
    ctx.new_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.55 * alpha)
    ctx.save()
    ctx.translate(x - r * 0.38, y - r * 0.45)
    ctx.scale(1.4, 0.8)
    ctx.arc(0, 0, r * 0.14, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()


def cilindro(ctx, x, y, w, h, cor, alpha=1.0, tampa=True):
    """Cilindro em pé (x = centro, y = topo) com sombreamento lateral e tampa elíptica."""
    g = cairo.LinearGradient(x - w / 2, 0, x + w / 2, 0)
    g.add_color_stop_rgba(0, *_escurecer(cor, 0.35), alpha)
    g.add_color_stop_rgba(0.35, *_clarear(cor, 0.25), alpha)
    g.add_color_stop_rgba(1, *_escurecer(cor, 0.45), alpha)
    e = w * 0.16
    ctx.new_path()
    ctx.move_to(x - w / 2, y)
    ctx.line_to(x - w / 2, y + h)
    ctx.save()
    ctx.translate(x, y + h)
    ctx.scale(w / 2, e)
    ctx.arc_negative(0, 0, 1, math.pi, 0)   # metade de baixo da elipse da base
    ctx.restore()
    ctx.line_to(x + w / 2, y)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()
    if tampa:
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(w / 2, e)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(*_clarear(cor, 0.3), alpha)
        ctx.fill()


def bloco_3d(ctx, x, y, w, h, prof, cor, alpha=1.0):
    """Bloco em projeção oblíqua: frente (x, y, w, h), topo e lateral com profundidade prof."""
    dx, dy = prof * 0.7, -prof * 0.5
    ctx.new_path()
    ctx.move_to(x, y)
    ctx.line_to(x + dx, y + dy)
    ctx.line_to(x + w + dx, y + dy)
    ctx.line_to(x + w, y)
    ctx.close_path()
    ctx.set_source_rgba(*_clarear(cor, 0.3), alpha)
    ctx.fill()
    ctx.move_to(x + w, y)
    ctx.line_to(x + w + dx, y + dy)
    ctx.line_to(x + w + dx, y + h + dy)
    ctx.line_to(x + w, y + h)
    ctx.close_path()
    ctx.set_source_rgba(*_escurecer(cor, 0.35), alpha)
    ctx.fill()
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgba(0, *cor, alpha)
    g.add_color_stop_rgba(1, *_escurecer(cor, 0.15), alpha)
    ctx.rectangle(x, y, w, h)
    ctx.set_source(g)
    ctx.fill()


def fundo_vivo(ctx, t, c1, c2, bokeh=(1, 1, 1), n=14):
    """Fundo em gradiente com manchas de luz desfocadas flutuando e vinheta: nunca fica parado."""
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *c1)
    g.add_color_stop_rgb(1, *c2)
    ctx.set_source(g)
    ctx.paint()
    for i in range(n):
        x = (_rnd(i) * W + t * (8 + 14 * _rnd(i, 1))) % (W + 200) - 100
        y = 200 + _rnd(i, 2) * 1300 + 30 * math.sin(t * 0.6 + i)
        brilho(ctx, x, y, 60 + 90 * _rnd(i, 3), bokeh, 0.06 + 0.06 * _rnd(i, 4))
    v = cairo.RadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.75)
    v.add_color_stop_rgba(0, 0, 0, 0, 0)
    v.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    ctx.set_source(v)
    ctx.paint()


# ---------- partículas ----------

def faiscas(ctx, t, x, y, n=40, cor=(1.0, 0.75, 0.3), vel=520, g=900, vida=1.2, seed=0, ang=(-math.pi, 0)):
    """Chuva contínua de faíscas saindo de (x, y), com gravidade e rastro."""
    for i in range(n):
        nasc = (_rnd(i, seed) * vida + t) % vida
        a = ang[0] + (ang[1] - ang[0]) * _rnd(i, seed + 1)
        v = vel * (0.5 + 0.5 * _rnd(i, seed + 2))
        px = x + math.cos(a) * v * nasc
        py = y + math.sin(a) * v * nasc + 0.5 * g * nasc * nasc
        vy = math.sin(a) * v + g * nasc
        vx = math.cos(a) * v
        f = 1 - nasc / vida
        ctx.set_source_rgba(*cor, f)
        ctx.set_line_width(4 * f + 1)
        ctx.move_to(px, py)
        ctx.line_to(px - vx * 0.03, py - vy * 0.03)
        ctx.stroke()


def estouro(ctx, t, x, y, cor=(1, 1, 1), r0=60, r1=260, n=14, dur=0.45, som="thud"):
    """Linhas de impacto saindo do ponto (estilo quadrinho) uma vez, em t = 0."""
    if som:
        core.evento_som(som, t)
    if t < 0 or t > dur:
        return
    k = t / dur
    ctx.set_line_width(10 * (1 - k) + 2)
    ctx.set_source_rgba(*cor, 1 - k)
    for i in range(n):
        a = i * 2 * math.pi / n + 0.2
        ra = r0 + (r1 - r0) * ease(k)
        rb = ra + 60 * (1 - k)
        ctx.move_to(x + ra * math.cos(a), y + ra * math.sin(a))
        ctx.line_to(x + rb * math.cos(a), y + rb * math.sin(a))
    ctx.stroke()


def confete(ctx, t, n=60, cores=((1, 0.3, 0.4), (1, 0.8, 0.2), (0.3, 0.8, 1), (0.4, 0.9, 0.5))):
    for i in range(n):
        x = _rnd(i) * W + 40 * math.sin(t * 2 + i)
        y = -40 + ((t * (180 + 120 * _rnd(i, 1)) + _rnd(i, 2) * H) % (H + 80))
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(t * 4 + i)
        ctx.scale(1, abs(math.sin(t * 5 + i)) + 0.2)
        ctx.set_source_rgb(*cores[i % len(cores)])
        ctx.rectangle(-9, -5, 18, 10)
        ctx.fill()
        ctx.restore()


def fumaca(ctx, t, x, y, n=10, cor=(0.85, 0.85, 0.9), sobe=160, alpha=0.25):
    for i in range(n):
        f = (t * 0.5 + _rnd(i)) % 1.0
        r = 30 + 70 * f
        ctx.new_path()
        ctx.set_source_rgba(*cor, alpha * (1 - f))
        ctx.arc(x + 40 * math.sin(i + t) * f, y - sobe * f * 2, r, 0, 2 * math.pi)
        ctx.fill()


def bolhas(ctx, t, x0, x1, y0, y1, n=30, r=8, alpha=0.7):
    for i in range(n):
        x = x0 + _rnd(i) * (x1 - x0) + 5 * math.sin(t * 3 + i)
        y = y1 - ((t * (100 + 80 * _rnd(i, 1)) + _rnd(i, 2) * (y1 - y0)) % (y1 - y0))
        ctx.new_path()
        ctx.set_source_rgba(1, 1, 1, alpha)
        ctx.arc(x, y, r * (0.5 + _rnd(i, 3)), 0, 2 * math.pi)
        ctx.fill()


# ---------- gatilhos de atenção ----------

def anel_destaque(ctx, t, x, y, r, cor=(1.0, 0.85, 0.2), som="pop"):
    """Círculo que se desenha em volta do detalhe e depois pulsa (use quando a voz citar o detalhe)."""
    if som:
        core.evento_som(som, t)
    if t < 0:
        return
    k = ease(t / 0.35)
    rr = r * (1 + 0.06 * math.sin(t * 7)) if t > 0.35 else r
    ctx.new_path()
    ctx.set_source_rgba(*cor, 0.95)
    ctx.set_line_width(9)
    ctx.arc(x, y, rr, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k)
    ctx.stroke()


def seta(ctx, t, x, y, ang=math.pi / 2, cor=(1.0, 0.85, 0.2), tam=90, som="pop"):
    """Seta grossa apontando para (x, y), vinda da direção `ang`, que entra com mola e fica balançando."""
    if som:
        core.evento_som(som, t)
    if t < 0:
        return
    k = max(mola(t, 0.4), 0.001)
    d = 30 + 14 * math.sin(t * 6)
    ctx.save()
    ctx.translate(x - math.cos(ang) * d, y - math.sin(ang) * d)
    ctx.rotate(ang)
    ctx.scale(k, k)
    ctx.new_path()
    ctx.move_to(0, 0)
    ctx.line_to(-tam * 0.55, -tam * 0.45)
    ctx.line_to(-tam * 0.55, -tam * 0.18)
    ctx.line_to(-tam * 1.2, -tam * 0.18)
    ctx.line_to(-tam * 1.2, tam * 0.18)
    ctx.line_to(-tam * 0.55, tam * 0.18)
    ctx.line_to(-tam * 0.55, tam * 0.45)
    ctx.close_path()
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.save()
    ctx.translate(4, 6)
    ctx.fill_preserve()
    ctx.restore()
    ctx.set_source_rgb(*cor)
    ctx.fill()
    ctx.restore()


def contador(ctx, t, x, y, fim, dur=1.2, ini=0, fmt="{:,.0f}", size=120, cor=(1, 1, 1), sufixo="", som="tick"):
    """Número correndo de ini até fim com tique a cada passo visível e um pop no final."""
    if t < 0:
        return
    k = 1 - (1 - min(1.0, t / dur)) ** 3
    v = ini + (fim - ini) * k
    if som and t < dur:
        passo = int(t / 0.08)
        core.evento_som(som, t - passo * 0.08)
    if t >= dur:
        core.evento_som("pop", t - dur)
    esc = 1 + 0.15 * max(0.0, 1 - abs(t - dur) / 0.15)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(esc, esc)
    text_center(ctx, fmt.format(v) + sufixo, 0, 0, size, cor, "ExtraBold")
    ctx.restore()


def texto_pop(ctx, t, palavras, x, y, size=110, cor=(1, 1, 1), intervalo=0.22, cor_destaque=None, destaque=-1,
              largura=900):
    """Tipografia cinética: palavras gigantes entrando uma a uma com mola (e pop), centralizadas em linhas."""
    core.font(ctx, size, "ExtraBold")
    linhas = core.wrap(ctx, palavras, largura)
    i = 0
    for li, ln in enumerate(linhas):
        larg = ctx.text_extents(" ".join(ln)).x_advance
        px = x - larg / 2
        for w in ln:
            tw = t - i * intervalo
            core.evento_som("pop", tw)
            adv = ctx.text_extents(w + " ").x_advance
            if tw >= 0:
                k = max(mola(tw, 0.4), 0.001)
                cx = px + ctx.text_extents(w).x_advance / 2
                cy = y + li * size * 1.05
                ctx.save()
                ctx.translate(cx, cy)
                ctx.scale(k, k)
                c = cor_destaque if (i == destaque and cor_destaque) else cor
                text_center(ctx, w, 0, 0, size, (0.02, 0.02, 0.05), "ExtraBold", alpha=0.5)
                text_center(ctx, w, -4, -5, size, c, "ExtraBold")
                ctx.restore()
                core.font(ctx, size, "ExtraBold")
            px += adv
            i += 1


def tremor(ctx, t, forca=18, dur=0.4, som="thud"):
    """Sacode a tela (chame antes de desenhar a cena; t = 0 no impacto)."""
    if som:
        core.evento_som(som, t)
    if 0 <= t < dur:
        f = forca * (1 - t / dur)
        ctx.translate(f * math.sin(t * 90), f * math.cos(t * 70))
