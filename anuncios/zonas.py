#!/usr/bin/env python3
"""Gera PNGs transparentes com as zonas seguras de cada plataforma, para sobrepor num quadro e conferir.

    python3 anuncios/zonas.py                      # -> anuncios/zonas/<plataforma>.png
    python3 anuncios/zonas.py --conferir peca.mp4 --em 3.0 --zona reels   # quadro da peça com a zona por cima

Vermelho = interface do app cobre; verde = área segura para texto, logo e CTA. Números em anuncios/FORMATOS.md.
"""
import argparse
import os
import subprocess

import cairo

AQUI = os.path.dirname(os.path.abspath(__file__))

# (largura, altura, topo, base, esquerda, direita) em fração da tela
ZONAS = {
    "reels": (1080, 1920, 0.14, 0.35, 0.06, 0.06),
    "stories": (1080, 1920, 0.14, 0.20, 0.0, 0.0),
    "shorts": (1080, 1920, 0.10, 0.25, 0.0, 0.10),
    "tiktok": (1080, 1920, 0.08, 0.25, 0.0, 0.13),  # aproximação: o oficial varia com a legenda (baixar os arquivos)
    "universal_9x16": (1080, 1920, 0.14, 0.35, 0.06, 0.12),
    "feed_4x5": (1080, 1350, 0.074, 0.074, 0.093, 0.093),
    "feed_1x1": (1080, 1080, 0.093, 0.093, 0.093, 0.093),
    "youtube_16x9": (1920, 1080, 0.08, 0.15, 0.05, 0.05),
}


def desenhar(nome):
    W, H, top, base, esq, dir_ = ZONAS[nome]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    c.set_source_rgba(0.9, 0.1, 0.1, 0.35)
    c.rectangle(0, 0, W, H)
    c.rectangle(W * esq, H * top, W * (1 - esq - dir_), H * (1 - top - base))
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    c.fill()
    c.set_source_rgba(0.1, 0.85, 0.3, 0.9)
    c.set_line_width(4)
    c.rectangle(W * esq, H * top, W * (1 - esq - dir_), H * (1 - top - base))
    c.stroke()
    c.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(H * 0.022)
    c.move_to(W * esq + 16, H * top + H * 0.03)
    c.show_text(nome.upper())
    pasta = os.path.join(AQUI, "zonas")
    os.makedirs(pasta, exist_ok=True)
    p = os.path.join(pasta, f"{nome}.png")
    s.write_to_png(p)
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--conferir", help="vídeo da peça")
    ap.add_argument("--em", type=float, default=2.0, help="segundo do quadro a conferir")
    ap.add_argument("--zona", default="universal_9x16", choices=list(ZONAS))
    a = ap.parse_args()
    if not a.conferir:
        for n in ZONAS:
            print(desenhar(n))
    else:
        z = desenhar(a.zona)
        W, H = ZONAS[a.zona][:2]
        out = os.path.splitext(a.conferir)[0] + f"_zona_{a.zona}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.em), "-i", a.conferir, "-i", z, "-frames:v", "1",
                        "-filter_complex", f"[0]scale={W}:{H}[v];[v][1]overlay", out], check=True)
        print(out)
