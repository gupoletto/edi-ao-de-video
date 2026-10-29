#!/usr/bin/env python3
"""Thumbnail do YouTube (1280x720) com quadros do próprio vídeo, na paleta do canal.

    python3 edicao/ferramentas/thumb.py edicao/bruto/video2.mkv --rosto 125.0 --espelhar --fundo 137.5 \\
        --titulo "CAÍ NUM *GOLPE*" --sub "no show do Iron Maiden" --selo "DIA 10/30"

- fundo: um quadro (cena, lugar) escurecido para o azul-marinho da paleta, à esquerda;
- rosto: um quadro com a expressão (ou --foto, uma foto que o usuário mandou), recortado em volta de --centro (frações x y do quadro), num cartão à
  direita (--zoom aproxima). --espelhar desfaz o espelho da câmera frontal (texto de camiseta/placa fica legível);
- --recortar: em vez do cartão, a pessoa recortada (rembg) com contorno branco de adesivo;
- --bilhete/--carimbo: um ingresso desenhado com carimbo torto, sob o título;
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
    busca = [] if t is None else ["-ss", str(t)]  # foto: sem -ss (numa imagem ele não devolve quadro)
    raw = subprocess.run(["ffmpeg", "-v", "error", *busca, "-i", fonte, "-frames:v", "1", "-f", "rawvideo",
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

    rosto = quadro(a.foto, None) if a.foto else quadro(a.fonte, a.rosto)
    if a.espelhar:
        rosto = rosto[:, ::-1]
    if a.recortar:
        pessoa(ctx, rosto, a, creme, navy)
    else:
        cartao(ctx, rosto, a, creme)
    texto_e_selo(ctx, a, navy, creme, cinza, taupe)

    nome = os.path.splitext(os.path.basename(a.fonte))[0]
    png = os.path.join(FINAL, f"{nome}_thumb.png")
    surf.write_to_png(png)
    jpg = png[:-4] + ".jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", jpg], check=True)
    print(f"pronto: {jpg} ({os.path.getsize(jpg) / 1e6:.1f} MB)")


def argb(rgba):
    """RGBA (PIL) -> superfície cairo ARGB32 pré-multiplicada."""
    a = np.asarray(rgba, np.float32)
    al = a[..., 3:4] / 255
    bgra = np.concatenate([a[..., 2::-1] * al, a[..., 3:4]], axis=2).round().astype(np.uint8)
    bgra = np.ascontiguousarray(bgra)
    h, w = bgra.shape[:2]
    return cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_ARGB32, w, h, w * 4), bgra


def pessoa(ctx, img, a, creme, navy):
    """Recorta a pessoa (rembg, modelo u2net_human_seg do GitHub) e cola como adesivo: contorno branco grosso,
    sombra marinho, sem fundo. A pessoa fica à direita, com a base da foto saindo pela borda de baixo."""
    from PIL import Image, ImageFilter
    from rembg import new_session, remove
    rgb = Image.fromarray(np.ascontiguousarray(img[..., 2::-1]))
    cut = remove(rgb, session=new_session("u2net_human_seg"))
    k = a.altura / cut.height
    cut = cut.resize((round(cut.width * k), round(cut.height * k)), Image.LANCZOS)
    alfa = cut.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    r = a.contorno
    borda = alfa.filter(ImageFilter.MaxFilter(2 * r + 1)).filter(ImageFilter.GaussianBlur(1.2))
    pad = r * 3
    lw, lh = cut.width + 2 * pad, cut.height + 2 * pad
    sombra = Image.new("L", (lw, lh), 0)
    sombra.paste(borda, (pad, pad))
    sombra = sombra.filter(ImageFilter.GaussianBlur(14))
    camada = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    camada.paste(Image.new("RGBA", (lw, lh), tuple(int(c * 255) for c in navy) + (0,)), (0, 0))
    camada.putalpha(sombra.point(lambda v: int(v * 0.8)))
    branco = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    branco.putalpha(borda)
    camada.alpha_composite(branco, (pad, pad))
    camada.alpha_composite(cut, (pad, pad))
    surf, _buf = argb(camada)
    x = W - lw + pad + a.desloc[0]
    y = H - lh + pad + a.desloc[1]
    ctx.set_source_surface(surf, x + 10, y + 14)  # sombra levemente para baixo
    ctx.paint()


def cartao(ctx, rosto, a, creme):
    """Cartão com o rosto, levemente inclinado."""
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


def bilhete(ctx, a, x, y, navy, creme, taupe):
    """Ingresso com picote e carimbo atravessado (ex.: "JÁ UTILIZADO")."""
    bw, bh = 470, 132
    ctx.save()
    ctx.translate(x + bw / 2, y + bh / 2)
    ctx.rotate(np.radians(-6))
    ctx.translate(-bw / 2, -bh / 2)
    arredondado(ctx, 0, 0, bw, bh, 12)
    ctx.set_source_rgb(*creme)
    ctx.fill()
    for cx in (0, bw):  # meias-luas do picote
        ctx.arc(cx, bh / 2, 16, 0, 2 * np.pi)
        ctx.set_source_rgb(*navy)
        ctx.fill()
    ctx.set_dash([8, 7])
    ctx.set_line_width(3)
    ctx.move_to(bw * 0.72, 12)
    ctx.line_to(bw * 0.72, bh - 12)
    ctx.set_source_rgba(*navy, 0.5)
    ctx.stroke()
    ctx.set_dash([])
    texto(ctx, "INGRESSO", 34, 50, 24, taupe)
    texto(ctx, a.bilhete, 34, 94, 30, navy)
    texto(ctx, "Nº 0001", bw * 0.72 + 24, 76, 22, navy)
    if a.carimbo:  # carimbo de borda dupla, torto por cima do ingresso
        ctx.translate(bw * 0.56, bh * 0.5)
        ctx.rotate(np.radians(-12))
        ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(36)
        e = ctx.text_extents(a.carimbo)
        cw, chh = e.x_advance + 40, 62
        cor = (0.69, 0.16, 0.18)  # vermelho de carimbo: o único fora da paleta, só aqui
        ctx.set_source_rgba(*cor, 0.92)
        for d, lw in ((0, 5), (8, 2)):
            arredondado(ctx, -cw / 2 - d, -chh / 2 - d, cw + 2 * d, chh + 2 * d, 10)
            ctx.set_line_width(lw)
            ctx.stroke()
        ctx.move_to(-e.x_advance / 2, 13)
        ctx.show_text(a.carimbo)
    ctx.restore()


def texto_e_selo(ctx, a, navy, creme, cinza, taupe):
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
    y = (260 if a.bilhete else 300) if len(linhas) > 1 else 360
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
        y += 70
    if a.bilhete:
        bilhete(ctx, a, x0 + 6, y + 10, navy, creme, taupe)


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
    ap.add_argument("--rosto", type=float, default=0.0, help="s do quadro com a expressão")
    ap.add_argument("--foto", help="em vez do quadro: uma foto (jpg/png) mandada pelo usuário")
    ap.add_argument("--fundo", type=float, required=True, help="s do quadro de fundo")
    ap.add_argument("--centro", type=float, nargs=2, default=[0.5, 0.4], help="centro do rosto (frações x y)")
    ap.add_argument("--centro-fundo", type=float, nargs=2, default=[0.5, 0.5])
    ap.add_argument("--zoom", type=float, default=1.0, help="aproxima o rosto no cartão (1.4 = 40 %% mais perto)")
    ap.add_argument("--espelhar", action="store_true")
    ap.add_argument("--recortar", action="store_true", help="pessoa recortada com contorno branco, sem cartão")
    ap.add_argument("--altura", type=int, default=780, help="altura da foto recortada na thumb (px)")
    ap.add_argument("--contorno", type=int, default=12, help="espessura do contorno branco (px)")
    ap.add_argument("--desloc", type=int, nargs=2, default=[0, 0], help="move a pessoa (px x y)")
    ap.add_argument("--bilhete", default="", help="ingresso desenhado sob o título (texto do evento)")
    ap.add_argument("--carimbo", default="", help="carimbo por cima do ingresso")
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--sub", default="")
    ap.add_argument("--selo", default="")
    ap.add_argument("--tamanho", type=int, default=104)
    montar(ap.parse_args())
