#!/usr/bin/env python3
"""Thumbnail "despertador" (episódio 17: perdeu o despertador, acordou 6:50 em vez de 5:50), no padrão do canal
(marinho, creme, taupe): a pessoa recortada com contorno branco, título grande à esquerda e um despertador de
campainha com a hora real grande e a hora planejada riscada embaixo, mais as atividades do dia.

    python3 edicao/ferramentas/thumb_despertador.py edicao/bruto/video9.mkv --rosto 163.5 \\
        --titulo "PERDI O|DESPERTADOR" --sub "Dia 17/30" --hora "6:50" --plano "5:50" --itens "Ombro · 9 séries"
Saída: edicao/final/<nome>_thumb.jpg (e .png).
"""
import argparse
import math
import os
import subprocess

import cairo

from comum import FINAL, preparar
from thumb import W, H, argb, arredondado, quadro, texto
from thumb_jogo import recorte
from thumb_relogio import CINZA, CREME, NAVY, TAUPE, fundo


def despertador(ctx, x, y, hora, plano, linhas, ang, escala=1.0):
    """Despertador de duas campainhas: mostrador escuro com a hora grande e a hora planejada riscada."""
    r = 150
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(ang))
    ctx.scale(escala, escala)
    for lado in (-1, 1):  # pés e campainhas
        ctx.save()
        ctx.rotate(lado * math.radians(38))
        ctx.set_source_rgb(*TAUPE)
        ctx.new_path()
        ctx.arc(0, -r - 22, 58, math.pi, 2 * math.pi)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
        ctx.set_line_width(14)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgb(*CINZA)
        ctx.move_to(lado * r * 0.55, r * 0.8)
        ctx.line_to(lado * r * 0.8, r * 1.12)
        ctx.stroke()
    ctx.set_line_width(10)  # martelo entre as campainhas
    ctx.set_source_rgb(*CINZA)
    ctx.move_to(0, -r)
    ctx.line_to(0, -r - 34)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(10, 12, r + 16, 0, 2 * math.pi)  # sombra
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.fill()
    ctx.new_sub_path()
    ctx.arc(0, 0, r + 16, 0, 2 * math.pi)
    ctx.set_source_rgb(*CREME)
    ctx.fill()
    ctx.new_sub_path()
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.set_source_rgb(0.02, 0.03, 0.08)
    ctx.fill()
    ctx.set_source_rgba(*CREME, 0.5)  # marcas das horas
    for k in range(12):
        a = k * math.pi / 6
        ctx.set_line_width(5 if k % 3 == 0 else 2.5)
        ctx.move_to(math.cos(a) * (r - 14), math.sin(a) * (r - 14))
        ctx.line_to(math.cos(a) * (r - 28), math.sin(a) * (r - 28))
        ctx.stroke()
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(92)
    e = ctx.text_extents(hora)
    texto(ctx, hora, -e.x_advance / 2, 22, 92, CREME)
    ctx.set_font_size(40)
    e = ctx.text_extents(plano)
    texto(ctx, plano, -e.x_advance / 2, 84, 40, CINZA)
    ctx.set_source_rgb(*TAUPE)  # risco na hora planejada
    ctx.set_line_width(6)
    ctx.move_to(-e.x_advance / 2 - 8, 70)
    ctx.line_to(e.x_advance / 2 + 8, 56)
    ctx.stroke()
    ctx.restore()
    for i, ln in enumerate(linhas):
        arredondado(ctx, x - 150, y + r * escala + 50 + i * 62, 300, 50, 25)
        ctx.set_source_rgba(*CREME, 0.12)
        ctx.fill()
        ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(28)
        e = ctx.text_extents(ln)
        texto(ctx, ln, x - e.x_advance / 2, y + r * escala + 86 + i * 62, 28, CREME)


def montar(a):
    preparar()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    fundo(ctx)
    import numpy as np
    img = quadro(a.fonte, a.rosto)
    img[..., :3] = np.clip(img[..., :3].astype(np.float32) * a.luz, 0, 255).astype(np.uint8)
    pessoa = recorte(img, a.altura, a.contorno, a.cortar_esq, a.cortar_dir)
    ps, _buf = argb(pessoa)
    ctx.set_source_surface(ps, W - pessoa.width + a.desloc[0], H - pessoa.height + a.desloc[1])
    ctx.paint()
    y = 150
    for i, ln in enumerate(a.titulo.split("|")):
        tam = a.tamanho
        texto(ctx, ln, 54 + 6, y + 6, tam, NAVY)
        texto(ctx, ln, 54, y, tam, CREME if i == 0 else TAUPE)
        y += tam * 0.98
    texto(ctx, a.sub, 60, y - 30, 40, CINZA, "Source Serif 4", cairo.FONT_WEIGHT_BOLD, italico=True)
    despertador(ctx, 290, y + 150, a.hora, a.plano, a.itens, -8, 0.78)
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
    ap.add_argument("--tamanho", type=int, default=104)
    ap.add_argument("--sub", default="")
    ap.add_argument("--itens", nargs="*", default=[])
    ap.add_argument("--altura", type=int, default=700)
    ap.add_argument("--contorno", type=int, default=8)
    ap.add_argument("--cortar-esq", type=float, default=0.0)
    ap.add_argument("--cortar-dir", type=float, default=0.0)
    ap.add_argument("--desloc", type=int, nargs=2, default=[30, 30])
    ap.add_argument("--hora", default="6:50")
    ap.add_argument("--plano", default="5:50")
    ap.add_argument("--luz", type=float, default=1.0, help="multiplica o brilho do quadro antes do recorte")
    montar(ap.parse_args())
