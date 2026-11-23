#!/usr/bin/env python3
"""Thumbnail "pôster synthwave" (anos 80): céu roxo, sol listrado, grade neon em perspectiva, a pessoa recortada
com contorno de neon, título cromado + palavra em letreiro de neon, e um placar de fliperama. Criada para o
episódio 13 (tema retro80).

    python3 edicao/ferramentas/thumb_retro.py edicao/bruto/video5.mkv --rosto 282.3 \\
        --cromado "FULL" --neon "PERNA" --sub "DIA 13/30" --placar "8,7 KM" "100 KG" "30 KM"
Saída: edicao/final/<nome>_thumb.jpg (e .png).
"""
import argparse
import math
import os
import subprocess

import cairo
import numpy as np

from comum import FINAL, preparar
from thumb import W, H, argb, quadro
from thumb_jogo import recorte

ROSA, CIANO, ROXO, NOITE = (1.0, 0.24, 0.65), (0.24, 0.91, 1.0), (0.30, 0.05, 0.40), (0.07, 0.02, 0.15)


def ceu(ctx, hor):
    g = cairo.LinearGradient(0, 0, 0, hor)
    g.add_color_stop_rgb(0, *NOITE)
    g.add_color_stop_rgb(0.55, *ROXO)
    g.add_color_stop_rgb(1, 0.85, 0.20, 0.45)
    ctx.rectangle(0, 0, W, hor)
    ctx.set_source(g)
    ctx.fill()
    rnd = np.random.default_rng(13)
    for _ in range(90):  # estrelas
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, hor * 0.6), rnd.uniform(0.6, 1.8)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, rnd.uniform(0.3, 0.9))
        ctx.fill()


def sol(ctx, cx, hor, R):
    for k, al in ((1.5, 0.10), (1.25, 0.18)):  # halo
        ctx.arc(cx, hor, R * k, math.pi, 2 * math.pi)
        ctx.set_source_rgba(1.0, 0.45, 0.55, al)
        ctx.fill()
    g = cairo.LinearGradient(0, hor - R, 0, hor)
    g.add_color_stop_rgb(0, 1.0, 0.86, 0.32)
    g.add_color_stop_rgb(1, *ROSA)
    ctx.save()
    ctx.arc(cx, hor, R, math.pi, 2 * math.pi)
    ctx.clip()
    ctx.rectangle(cx - R, hor - R, 2 * R, R)
    ctx.set_source(g)
    ctx.fill()
    for i in range(7):  # faixas cortando a metade de baixo do sol
        y = hor - R * 0.06 - i * R * 0.11
        ctx.rectangle(cx - R, y - R * 0.022 * (7 - i) * 0.5, 2 * R, R * 0.022 * (7 - i))
    ctx.set_source_rgb(0.62, 0.12, 0.42)
    ctx.fill()
    ctx.restore()


def grade(ctx, hor):
    ctx.rectangle(0, hor, W, H - hor)
    g = cairo.LinearGradient(0, hor, 0, H)
    g.add_color_stop_rgb(0, 0.14, 0.03, 0.22)
    g.add_color_stop_rgb(1, *NOITE)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_line_width(2)
    ctx.set_source_rgba(*CIANO, 0.9)
    for i in range(-16, 17):
        ctx.move_to(W / 2 + i * W * 0.018, hor)
        ctx.line_to(W / 2 + i * W * 0.2, H)
    for j in range(1, 9):
        y = hor + (H - hor) * (j / 9) ** 1.8
        ctx.move_to(0, y)
        ctx.line_to(W, y)
    ctx.stroke()
    ctx.rectangle(0, hor - 1, W, 3)  # linha do horizonte acesa
    ctx.set_source_rgba(*ROSA, 1)
    ctx.fill()


def contorno_neon(pessoa_rgba, cor, largura=7, brilho=22):
    """Contorno colorido + brilho atrás da pessoa recortada (RGBA PIL). Devolve um RGBA maior por causa do brilho."""
    from PIL import Image, ImageFilter
    a = pessoa_rgba.getchannel("A")
    m = brilho * 2
    tela = Image.new("RGBA", (pessoa_rgba.width + 2 * m, pessoa_rgba.height + 2 * m), (0, 0, 0, 0))
    am = Image.new("L", tela.size, 0)
    am.paste(a, (m, m))
    borda = am.filter(ImageFilter.MaxFilter(largura * 2 + 1))
    glow = borda.filter(ImageFilter.GaussianBlur(brilho))
    c = tuple(int(v * 255) for v in cor)
    camada_glow = Image.new("RGBA", tela.size, c + (0,))
    camada_glow.putalpha(glow)
    camada_borda = Image.new("RGBA", tela.size, c + (0,))
    camada_borda.putalpha(borda)
    tela = Image.alpha_composite(tela, camada_glow)
    tela = Image.alpha_composite(tela, camada_borda)
    corpo = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    corpo.paste(pessoa_rgba, (m, m))
    return Image.alpha_composite(tela, corpo), m


def cromado(ctx, s, x, y, tam):
    ctx.select_font_face("Audiowide", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(tam)
    e = ctx.text_extents(s)
    ctx.move_to(x + 6, y + 6)
    ctx.text_path(s)
    ctx.set_source_rgba(0, 0, 0, 0.55)
    ctx.fill()
    ctx.move_to(x, y)
    ctx.text_path(s)
    g = cairo.LinearGradient(0, y - e.height, 0, y)
    for p, c in ((0, (0.98, 0.98, 1.0)), (0.45, (0.55, 0.75, 0.95)), (0.5, (0.18, 0.10, 0.30)),
                 (0.62, (0.95, 0.55, 0.85)), (1, (1.0, 0.95, 1.0))):
        g.add_color_stop_rgb(p, *c)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.5)
    ctx.stroke()
    return e.x_advance


def letreiro_neon(ctx, s, x, y, tam, cor):
    ctx.select_font_face("Monoton", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(tam)
    for larg, al in ((18, 0.12), (10, 0.25), (5, 0.5)):  # brilho em camadas
        ctx.move_to(x, y)
        ctx.text_path(s)
        ctx.set_source_rgba(*cor, al)
        ctx.set_line_width(larg)
        ctx.stroke()
    ctx.move_to(x, y)
    ctx.text_path(s)
    ctx.set_source_rgb(1, 0.92, 0.97)
    ctx.fill()
    return ctx.text_extents(s).x_advance


def pixel(ctx, s, x, y, tam, cor, sombra=True):
    ctx.select_font_face("Press Start 2P", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(tam)
    if sombra:
        ctx.move_to(x + 3, y + 3)
        ctx.set_source_rgba(0, 0, 0, 0.7)
        ctx.show_text(s)
    ctx.move_to(x, y)
    ctx.set_source_rgb(*cor)
    ctx.show_text(s)
    return ctx.text_extents(s).x_advance


def montar(a):
    preparar()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    hor = H * 0.64
    ceu(ctx, hor)
    sol(ctx, W * 0.72, hor, H * 0.42)
    grade(ctx, hor)
    from PIL import Image
    img = quadro(a.fonte, a.rosto)
    p = recorte(img, a.altura, 1, a.cortar_esq, a.cortar_dir)  # contorno mínimo (0 quebra o MaxFilter): o neon cobre
    p = Image.fromarray(np.asarray(p)) if not hasattr(p, "getchannel") else p
    p_neon, m = contorno_neon(p, ROSA)
    ps, _buf = argb(p_neon)
    px = W - p.width + a.desloc[0] - m
    py = H - p.height + a.desloc[1] - m
    ctx.set_source_surface(ps, px, py)
    ctx.paint()
    # título à esquerda
    x0 = 46
    pixel(ctx, "PLAY", x0, 64, 22, (1, 1, 1))
    ctx.move_to(x0 + 104, 42)
    ctx.line_to(x0 + 124, 53)
    ctx.line_to(x0 + 104, 64)
    ctx.close_path()
    ctx.fill()
    cromado(ctx, a.cromado, x0, 238, 150)
    letreiro_neon(ctx, a.neon, x0 + 6, 372, 118, ROSA)
    pixel(ctx, a.sub, x0 + 10, 440, 30, CIANO)
    # placar de fliperama: as 3 fases do dia
    if a.placar:
        y = H - 96
        x = x0
        for i, item in enumerate(a.placar, 1):
            rot = f"FASE {i}"
            wbox = max(170, 26 * len(item) + 40)
            ctx.rectangle(x, y - 46, wbox, 86)
            ctx.set_source_rgba(*NOITE, 0.85)
            ctx.fill_preserve()
            ctx.set_source_rgb(*CIANO)
            ctx.set_line_width(3)
            ctx.stroke()
            pixel(ctx, rot, x + 16, y - 16, 14, CIANO, sombra=False)
            pixel(ctx, item, x + 16, y + 22, 22, (1, 0.95, 0.4), sombra=False)
            x += wbox + 16
    nome = os.path.splitext(os.path.basename(a.fonte))[0]
    png = os.path.join(FINAL, f"{nome}_thumb.png")
    surf.write_to_png(png)
    jpg = png[:-4] + ".jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", jpg], check=True)
    print(f"pronto: {jpg}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--rosto", type=float, required=True)
    ap.add_argument("--cromado", default="FULL")
    ap.add_argument("--neon", default="PERNA")
    ap.add_argument("--sub", default="DIA 1/30")
    ap.add_argument("--placar", nargs="*", default=[])
    ap.add_argument("--altura", type=int, default=700)
    ap.add_argument("--cortar-esq", type=float, default=0.0)
    ap.add_argument("--cortar-dir", type=float, default=0.0)
    ap.add_argument("--desloc", type=int, nargs=2, default=[30, 40])
    montar(ap.parse_args())
