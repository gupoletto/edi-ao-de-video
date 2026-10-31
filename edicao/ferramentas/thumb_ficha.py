#!/usr/bin/env python3
"""Thumbnail "ficha policial" (mugshot): a pessoa recortada na frente da régua de altura, com a placa de
identificação, o carimbo e o título. Criada para o episódio 12 (fantasia de gangster no Halloween).

    python3 edicao/ferramentas/thumb_ficha.py edicao/bruto/video4.mkv --rosto 254.7 \\
        --titulo "GANGSTER|POR UMA NOITE" --placa "MELHORANDO MINHA VIDA" --numero "DIA 12/30" --carimbo "FICHADO"
Saída: edicao/final/<nome>_thumb.jpg (e .png).
"""
import argparse
import math
import os
import subprocess

import cairo

from comum import FINAL, preparar
from elementos import PALETA
from thumb import W, H, arredondado, argb, quadro, texto
from thumb_jogo import recorte

NAVY, CREME, CINZA, TAUPE = (PALETA[k] for k in ("fundo", "tinta", "suave", "destaque"))
CARTAO = PALETA["cartao"]


def regua(ctx, x0, x1):
    """Parede de delegacia: faixas de altura com os números em centímetros."""
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *CARTAO)
    g.add_color_stop_rgb(1, *NAVY)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.paint()
    for i, cm in enumerate(range(200, 130, -10)):
        y = 70 + i * 92
        ctx.set_source_rgba(*CREME, 0.55 if cm % 20 == 0 else 0.3)
        ctx.rectangle(x0, y, x1 - x0, 4 if cm % 20 == 0 else 2)
        ctx.fill()
        texto(ctx, f"{cm}", x1 - 70, y - 10, 26, CINZA)
        for k in range(1, 5):  # traços menores
            ctx.rectangle(x1 - 30, y + k * 18, 30, 2)
        ctx.set_source_rgba(*CREME, 0.25)
        ctx.fill()
    luz = cairo.RadialGradient(x0 + (x1 - x0) * 0.55, H * 0.35, 30, x0 + (x1 - x0) * 0.55, H * 0.35, H * 0.8)
    luz.add_color_stop_rgba(0, *CREME, 0.18)  # luz de flash atrás da cabeça
    luz.add_color_stop_rgba(1, *CREME, 0)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(luz)
    ctx.fill()


def placa(ctx, cx, y, linha1, linha2):
    w, h = 470, 150
    ctx.save()
    ctx.translate(cx, y)
    ctx.rotate(math.radians(-2))
    arredondado(ctx, -w / 2 - 6, -6, w + 12, h + 12, 10)
    ctx.set_source_rgb(0.05, 0.05, 0.07)
    ctx.fill()
    arredondado(ctx, -w / 2, 0, w, h, 6)
    ctx.set_source_rgb(*CREME)
    ctx.fill()
    ctx.select_font_face("DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    for s, tam, yy in ((linha1, 26, 50), (linha2, 60, 120)):
        ctx.set_font_size(tam)
        e = ctx.text_extents(s)
        ctx.move_to(-e.x_advance / 2, yy)
        ctx.set_source_rgb(*NAVY)
        ctx.show_text(s)
    ctx.restore()


def carimbo(ctx, s, x, y):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(-12))
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(58)
    e = ctx.text_extents(s)
    w, h = e.x_advance + 50, 86
    cor = (0.72, 0.16, 0.18)  # vermelho de carimbo, fora da paleta só aqui
    ctx.set_source_rgba(*cor, 0.93)
    for d, lw in ((0, 6), (10, 2.5)):
        arredondado(ctx, -w / 2 - d, -h / 2 - d, w + 2 * d, h + 2 * d, 10)
        ctx.set_line_width(lw)
        ctx.stroke()
    ctx.move_to(-e.x_advance / 2, 21)
    ctx.show_text(s)
    ctx.restore()


def montar(a):
    preparar()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    regua(ctx, 560, W)
    pessoa = recorte(quadro(a.fonte, a.rosto), a.altura, a.contorno, a.cortar_esq, a.cortar_dir)
    ps, _buf = argb(pessoa)
    px = W - pessoa.width + a.desloc[0]
    ctx.set_source_surface(ps, px, H - pessoa.height + a.desloc[1])
    ctx.paint()
    placa(ctx, px + pessoa.width / 2 - 10, H - 190, a.placa, a.numero)
    # título à esquerda, sobre uma faixa escura para ler bem
    g = cairo.LinearGradient(0, 0, 640, 0)
    g.add_color_stop_rgba(0, *NAVY, 0.96)
    g.add_color_stop_rgba(0.75, *NAVY, 0.85)
    g.add_color_stop_rgba(1, *NAVY, 0)
    ctx.rectangle(0, 0, 640, H)
    ctx.set_source(g)
    ctx.fill()
    linhas = a.titulo.split("|")
    y = 250
    for i, ln in enumerate(linhas):
        tam = 112 if i == 0 else 64
        if i == 0:
            texto(ctx, ln, 58 + 7, y + 7, tam, TAUPE)
        texto(ctx, ln, 58, y, tam, CREME if i == 0 else TAUPE)
        y += tam * 1.05
    if a.sub:
        texto(ctx, a.sub, 62, y + 30, 40, CINZA, "Source Serif 4", cairo.FONT_WEIGHT_BOLD, italico=True)
    if a.carimbo:
        carimbo(ctx, a.carimbo, 300, H - 150)
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
    ap.add_argument("--titulo", required=True, help='linhas separadas por "|"')
    ap.add_argument("--sub", default="")
    ap.add_argument("--placa", default="MELHORANDO MINHA VIDA")
    ap.add_argument("--numero", default="DIA 1/30")
    ap.add_argument("--carimbo", default="")
    ap.add_argument("--altura", type=int, default=690)
    ap.add_argument("--contorno", type=int, default=0)
    ap.add_argument("--cortar-esq", type=float, default=0.0)
    ap.add_argument("--cortar-dir", type=float, default=0.0)
    ap.add_argument("--desloc", type=int, nargs=2, default=[40, 30])
    montar(ap.parse_args())
