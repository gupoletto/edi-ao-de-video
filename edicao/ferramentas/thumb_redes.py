#!/usr/bin/env python3
"""Thumbnail "ajustes do celular" (episódio 14: de volta às redes, só para criar), derivada da "ficha de treino" no padrão do canal (marinho, creme, taupe): a pessoa recortada com contorno branco,
título grande à esquerda e uma ficha de papel com as atividades do dia marcadas, mais um carimbo de nota.
Criada para o episódio 13 ("dia full perna").

    python3 edicao/ferramentas/thumb_treino.py edicao/bruto/video5.mkv --rosto 282.3 \\
        --titulo "FULL|PERNA" --sub "Dia 13/30" --itens "Corrida · 8,7 km" "Perna · até 100 kg" "Pedal · 30 km" \\
        --carimbo "NOTA 10"
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


def fundo(ctx):
    g = cairo.RadialGradient(W * 0.72, H * 0.4, 40, W * 0.72, H * 0.4, W * 0.75)
    g.add_color_stop_rgb(0, *CARTAO)
    g.add_color_stop_rgb(1, *NAVY)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.paint()
    ctx.set_source_rgba(*CREME, 0.05)  # pauta leve de caderno ao fundo
    for y in range(40, H, 46):
        ctx.rectangle(0, y, W, 2)
    ctx.fill()


def chave(ctx, x, y, ligada):
    """Chave liga/desliga de configurações (taupe = ligada, cinza = desligada)."""
    w, h = 96, 52
    arredondado(ctx, x, y, w, h, h / 2)
    ctx.set_source_rgb(*(TAUPE if ligada else CINZA))
    ctx.fill()
    cx = x + (w - h / 2) if ligada else x + h / 2
    ctx.arc(cx, y + h / 2, h / 2 - 6, 0, 2 * math.pi)
    ctx.set_source_rgb(*CREME)
    ctx.fill()


def celular(ctx, x, y, linhas, ang):
    """Celular inclinado com a tela de ajustes: uma chave por linha ("Criar:1", "Consumir:0")."""
    w, h = 420, 330
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(ang))
    arredondado(ctx, 10, 12, w, h, 48)  # sombra
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.fill()
    arredondado(ctx, 0, 0, w, h, 48)
    ctx.set_source_rgb(*CREME)
    ctx.fill()
    arredondado(ctx, 14, 14, w - 28, h - 28, 36)
    ctx.set_source_rgb(*NAVY)
    ctx.fill()
    arredondado(ctx, w / 2 - 50, 26, 100, 22, 11)  # ilha da câmera
    ctx.set_source_rgb(0.02, 0.03, 0.08)
    ctx.fill()
    texto(ctx, "REDES SOCIAIS", 44, 96, 30, TAUPE)
    for i, ln in enumerate(linhas):
        nome, liga = ln.rsplit(":", 1)
        yy = 128 + i * 96
        ctx.set_source_rgba(*CREME, 0.12)
        ctx.rectangle(40, yy + 84, w - 80, 2)
        ctx.fill()
        texto(ctx, nome, 44, yy + 56, 40, CREME)
        chave(ctx, w - 44 - 96, yy + 20, liga.strip() == "1")
    ctx.restore()


def carimbo(ctx, s, x, y):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(-14))
    r = 74
    ctx.new_path()  # sem isso o arco começa ligado ao último ponto desenhado (o traço do "check")
    ctx.set_source_rgba(*TAUPE, 0.95)
    for rr, lw in ((r, 6), (r - 12, 2.5)):
        ctx.new_sub_path()
        ctx.arc(0, 0, rr, 0, 2 * math.pi)
        ctx.set_line_width(lw)
        ctx.stroke()
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    for k, (parte, tam) in enumerate(((s.split()[0], 24), (" ".join(s.split()[1:]), 56))):
        ctx.set_font_size(tam)
        e = ctx.text_extents(parte)
        ctx.move_to(-e.x_advance / 2, -10 if k == 0 else 38)
        ctx.show_text(parte)
    ctx.restore()


def montar(a):
    preparar()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    fundo(ctx)
    import numpy as np
    img = quadro(a.fonte, a.rosto)
    img[..., :3] = np.clip(img[..., :3].astype(np.float32) * a.luz, 0, 255).astype(np.uint8)  # rosto mais claro
    pessoa = recorte(img, a.altura, a.contorno, a.cortar_esq, a.cortar_dir)
    ps, _buf = argb(pessoa)
    px = W - pessoa.width + a.desloc[0]
    ctx.set_source_surface(ps, px, H - pessoa.height + a.desloc[1])
    ctx.paint()
    linhas = a.titulo.split("|")
    y = 150
    for i, ln in enumerate(linhas):
        tam = 118
        cor = CREME if i == 0 else TAUPE
        texto(ctx, ln, 54 + 6, y + 6, tam, NAVY)
        texto(ctx, ln, 54, y, tam, cor)
        y += tam * 0.98
    texto(ctx, a.sub, 60, y - 30, 40, CINZA, "Source Serif 4", cairo.FONT_WEIGHT_BOLD, italico=True)
    celular(ctx, 70, y + 12, a.itens, -4)
    if a.carimbo:
        carimbo(ctx, a.carimbo, 470, y + 10)
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
    ap.add_argument("--itens", nargs="*", default=[])
    ap.add_argument("--carimbo", default="")
    ap.add_argument("--altura", type=int, default=650)
    ap.add_argument("--contorno", type=int, default=8)
    ap.add_argument("--cortar-esq", type=float, default=0.0)
    ap.add_argument("--cortar-dir", type=float, default=0.0)
    ap.add_argument("--desloc", type=int, nargs=2, default=[30, 30])
    ap.add_argument("--luz", type=float, default=1.0, help="multiplica o brilho do quadro antes do recorte")
    montar(ap.parse_args())
