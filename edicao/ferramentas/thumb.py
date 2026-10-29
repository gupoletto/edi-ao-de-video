#!/usr/bin/env python3
"""Thumbnail do YouTube (1280x720) com quadros do próprio vídeo, na paleta do canal.

    python3 edicao/ferramentas/thumb.py edicao/bruto/video2.mkv --rosto 125.0 --espelhar --fundo 137.5 \\
        --titulo "CAÍ NUM *GOLPE*" --sub "no show do Iron Maiden" --selo "DIA 10/30"

- fundo: um quadro (cena, lugar) escurecido para o azul-marinho da paleta, à esquerda;
- rosto: um quadro com a expressão, recortado em volta de --centro (frações x y do quadro), num cartão à
  direita (--zoom aproxima). --espelhar desfaz o espelho da câmera frontal (texto de camiseta/placa fica legível);
- titulo: no máximo 4 palavras; a parte entre *asteriscos* ganha a tarja de destaque. sub e selo são opcionais.
Saída: edicao/final/<nome>_thumb.jpg (e .png).
"""
import argparse
import os
import subprocess

import cairo
import numpy as np

from comum import FINAL, preparar
from elementos import PALETA

W, H = 1280, 720


def quadro(fonte, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", fonte, "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "bgra", "-"], capture_output=True, check=True).stdout
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", fonte], capture_output=True, text=True, check=True).stdout.split(",")
    w, h = int(r[0]), int(r[1])
    a = np.frombuffer(raw, np.uint8).reshape(h, w, 4).copy()
    return a


def superficie(a):
    a = np.ascontiguousarray(a)
    h, w = a.shape[:2]
    return cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_RGB24, w, h, w * 4), a


def cobrir(ctx, img, x, y, w, h, cx=0.5, cy=0.5, zoom=1.0):
    """Desenha img cobrindo o retângulo (como object-fit: cover), centrado em (cx, cy) da imagem."""
    s, _ = superficie(img)
    ih, iw = img.shape[:2]
    k = max(w / iw, h / ih) * zoom
    ox = min(0, max(w - iw * k, w / 2 - iw * k * cx))
    oy = min(0, max(h - ih * k, h / 2 - ih * k * cy))
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    ctx.translate(x + ox, y + oy)
    ctx.scale(k, k)
    ctx.set_source_surface(s, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BEST)
    ctx.paint()
    ctx.restore()


def texto(ctx, s, x, y, tam, cor, fonte="Poppins", peso=cairo.FONT_WEIGHT_BOLD, italico=False):
    ctx.select_font_face(fonte, cairo.FONT_SLANT_ITALIC if italico else cairo.FONT_SLANT_NORMAL, peso)
    ctx.set_font_size(tam)
    ctx.move_to(x, y)
    ctx.set_source_rgb(*cor)
    ctx.show_text(s)
    return ctx.text_extents(s).x_advance


def arredondado(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        ctx.arc(cx, cy, r, np.radians(a0), np.radians(a0 + 90))
    ctx.close_path()


def montar(a):
    preparar()
    navy, creme, cinza, taupe = (PALETA[k] for k in ("fundo", "tinta", "suave", "destaque"))
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(*navy)
    ctx.paint()

    # fundo: a cena, puxada para o azul-marinho e escurecida à esquerda, onde fica o texto
    cobrir(ctx, quadro(a.fonte, a.fundo), 0, 0, W, H, *a.centro_fundo)
    g = cairo.LinearGradient(0, 0, W, 0)
    g.add_color_stop_rgba(0, *navy, 0.92)
    g.add_color_stop_rgba(0.55, *navy, 0.55)
    g.add_color_stop_rgba(1, *navy, 0.25)
    ctx.set_source(g)
    ctx.paint()

    # cartão com o rosto, levemente inclinado
    rosto = quadro(a.fonte, a.rosto)
    if a.espelhar:
        rosto = rosto[:, ::-1]
    cw, ch = 470, 640
    ctx.save()
    ctx.translate(W - cw / 2 - 50, H / 2 + 10)
    ctx.rotate(np.radians(3))
    arredondado(ctx, -cw / 2 - 10, -ch / 2 - 10, cw + 20, ch + 20, 26)
    ctx.set_source_rgb(*creme)
    ctx.fill()
    arredondado(ctx, -cw / 2, -ch / 2, cw, ch, 18)
    ctx.clip()
    cx = 1 - a.centro[0] if a.espelhar else a.centro[0]
    cobrir(ctx, rosto, -cw / 2, -ch / 2, cw, ch, cx, a.centro[1], a.zoom)
    ctx.restore()

    # selo
    x0 = 64
    if a.selo:
        ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(34)
        sw = ctx.text_extents(a.selo).x_advance
        arredondado(ctx, x0, 70, sw + 44, 60, 30)
        ctx.set_source_rgb(*creme)
        ctx.fill()
        texto(ctx, a.selo, x0 + 22, 112, 34, navy)

    # título: até 2 linhas; *destaque* com tarja taupe e texto marinho
    linhas = a.titulo.split("|") if "|" in a.titulo else _quebra(a.titulo)
    y = 300 if len(linhas) > 1 else 360
    for ln in linhas:
        x = x0
        partes = ln.split("*")
        for k, p in enumerate(partes):
            if not p:
                continue
            ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(a.tamanho)
            ext = ctx.text_extents(p.strip())
            if k % 2:  # destaque
                arredondado(ctx, x - 14, y - a.tamanho * 0.82, ext.x_advance + 28, a.tamanho * 1.02, 14)
                ctx.set_source_rgb(*taupe)
                ctx.fill()
                x += texto(ctx, p.strip(), x, y, a.tamanho, navy) + a.tamanho * 0.32
            else:
                x += texto(ctx, p.strip(), x, y, a.tamanho, creme) + a.tamanho * 0.25
        y += a.tamanho * 1.12
    if a.sub:
        texto(ctx, a.sub, x0, y + 18, 50, cinza, "Source Serif 4", cairo.FONT_WEIGHT_BOLD, italico=True)

    nome = os.path.splitext(os.path.basename(a.fonte))[0]
    png = os.path.join(FINAL, f"{nome}_thumb.png")
    surf.write_to_png(png)
    jpg = png[:-4] + ".jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", jpg], check=True)
    print(f"pronto: {jpg} ({os.path.getsize(jpg) / 1e6:.1f} MB)")


def _quebra(t):
    """Duas linhas equilibradas para títulos de 3+ palavras."""
    ws = t.split()
    if len(ws) < 3:
        return [t]
    meio = (len(ws) + 1) // 2
    return [" ".join(ws[:meio]), " ".join(ws[meio:])]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--rosto", type=float, required=True, help="s do quadro com a expressão")
    ap.add_argument("--fundo", type=float, required=True, help="s do quadro de fundo")
    ap.add_argument("--centro", type=float, nargs=2, default=[0.5, 0.4], help="centro do rosto (frações x y)")
    ap.add_argument("--centro-fundo", type=float, nargs=2, default=[0.5, 0.5])
    ap.add_argument("--zoom", type=float, default=1.0, help="aproxima o rosto no cartão (1.4 = 40 %% mais perto)")
    ap.add_argument("--espelhar", action="store_true")
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--sub", default="")
    ap.add_argument("--selo", default="")
    ap.add_argument("--tamanho", type=int, default=104)
    montar(ap.parse_args())
