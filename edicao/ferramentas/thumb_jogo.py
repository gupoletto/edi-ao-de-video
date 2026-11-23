#!/usr/bin/env python3
"""Thumbnail no estilo HUD de videogame: o dia do desafio como um nível que sobe.

    python3 edicao/ferramentas/thumb_jogo.py edicao/bruto/video3.mkv --rosto 52.4 --nivel 11 --total 30 \\
        --conquistas "+2 KM DE CORRIDA" "+TREINO DE BRAÇO" "+JANTA CASEIRA" --item 328.5 --item-centro 0.6 0.6 \\
        --item-raio 0.17 --item-rotulo "ITEM DO DIA"

- você recortado (rembg) com contorno branco, à direita;
- "NÍVEL N" grande com sombra 3D e a barra de XP do desafio (N de total) em blocos;
- conquistas do dia em placas inclinadas com "+XP";
- um "item" (ex.: o prato da janta) recortado em círculo, com brilho e etiqueta.
Saída: edicao/final/<nome>_thumb.jpg (e .png).
"""
import argparse
import math
import os
import subprocess

import cairo
import numpy as np

from comum import FINAL, preparar
from elementos import PALETA
from thumb import W, H, arredondado, argb, quadro, superficie, texto

NAVY, CREME, CINZA, TAUPE = (PALETA[k] for k in ("fundo", "tinta", "suave", "destaque"))
CARTAO = PALETA["cartao"]


def fundo(ctx):
    g = cairo.LinearGradient(0, 0, W, H)
    g.add_color_stop_rgb(0, *CARTAO)
    g.add_color_stop_rgb(1, *NAVY)
    ctx.set_source(g)
    ctx.paint()
    cx, cy = W * 0.72, H * 0.42  # raios de luz atrás do personagem
    for i in range(18):
        a = i * 2 * math.pi / 18
        ctx.move_to(cx, cy)
        ctx.arc(cx, cy, W, a, a + 0.09)
        ctx.close_path()
    ctx.set_source_rgba(*CREME, 0.06)
    ctx.fill()
    for x in range(0, W, 26):  # grade de pixels
        for y in range(0, H, 26):
            ctx.new_sub_path()
            ctx.arc(x, y, 1.3, 0, 2 * math.pi)
    ctx.set_source_rgba(*CINZA, 0.16)
    ctx.fill()
    halo = cairo.RadialGradient(cx, cy, 20, cx, cy, H * 0.6)
    halo.add_color_stop_rgba(0, *TAUPE, 0.45)
    halo.add_color_stop_rgba(1, *TAUPE, 0)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(halo)
    ctx.fill()


def recorte(img, altura, contorno, cortar_esq=0.0, cortar_dir=0.0, remover_laranja=False):
    """Pessoa recortada com contorno branco; cortar_esq/dir tiram parte das laterais (o braço da selfie)."""
    from PIL import Image, ImageEnhance, ImageFilter
    from rembg import new_session, remove
    from scipy import ndimage
    rgb = Image.fromarray(np.ascontiguousarray(img[..., 2::-1]))
    rgb = ImageEnhance.Contrast(ImageEnhance.Brightness(rgb).enhance(0.94)).enhance(1.18)  # câmera estourada
    cut = remove(rgb, session=new_session("u2net_human_seg"))
    if remover_laranja:  # objeto laranja/vermelho saturado colado no contorno (fruta, pimenta no fundo)
        hsv = np.array(cut.convert("RGB").convert("HSV")).astype(np.float32)
        a = np.array(cut.getchannel("A"))
        perto_da_borda = ndimage.distance_transform_edt(a > 128) < 60  # só perto do contorno: o rosto fica intacto
        a[perto_da_borda & (hsv[..., 1] > 170) & ((hsv[..., 0] < 22) | (hsv[..., 0] > 245)) & (hsv[..., 2] > 110)] = 0
        a = ndimage.binary_fill_holes(ndimage.binary_opening(a > 128, iterations=3)).astype(np.uint8) * 255
        cut.putalpha(Image.fromarray(a))
    from scipy import ndimage  # fica só a maior mancha (a pessoa); some objeto solto que o recorte pegou junto
    a = np.array(cut.getchannel("A"))
    rot, n = ndimage.label(a > 128)
    if n > 1:
        maior = 1 + int(np.argmax(ndimage.sum(np.ones_like(a), rot, range(1, n + 1))))
        a[rot != maior] = 0
    a = np.where(ndimage.binary_fill_holes(a > 128), np.maximum(a, 255 * (a <= 128)), a).astype(np.uint8)
    cut.putalpha(Image.fromarray(a))
    bb = cut.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox()
    w = bb[2] - bb[0]
    cut = cut.crop((int(bb[0] + w * cortar_esq), bb[1], int(bb[2] - w * cortar_dir), bb[3]))
    k = altura / cut.height
    cut = cut.resize((round(cut.width * k), round(cut.height * k)), Image.LANCZOS)
    alfa = cut.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    pad = contorno * 3
    borda = Image.new("L", (cut.width + 2 * pad, cut.height + 2 * pad), 0)
    borda.paste(alfa, (pad, pad))
    borda = borda.filter(ImageFilter.MaxFilter(2 * contorno + 1)).filter(ImageFilter.GaussianBlur(1.0))
    if cortar_esq:  # onde a foto foi cortada, sem contorno e com a borda esmaecendo
        b = np.array(borda)
        b[:, :pad + 40] = 0
        borda = Image.fromarray(b)
        a = np.array(cut.getchannel("A")).astype(np.float32)
        a[:, :60] *= np.linspace(0, 1, 60)[None, :]
        cut.putalpha(Image.fromarray(a.astype(np.uint8)))
    camada = Image.new("RGBA", borda.size, (0, 0, 0, 0))
    sombra = Image.new("RGBA", borda.size, tuple(int(c * 255) for c in NAVY) + (0,))
    sombra.putalpha(borda.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.85)))
    camada.alpha_composite(sombra, (12, 16))
    branco = Image.new("RGBA", borda.size, (255, 255, 255, 255))
    branco.putalpha(borda)
    camada.alpha_composite(branco)
    camada.alpha_composite(cut, (pad, pad))
    return camada


def nivel(ctx, n, total, x, y, serie):
    texto(ctx, serie, x + 4, y - 118, 24, CINZA)
    s = f"NÍVEL {n}"
    for d, cor in ((9, TAUPE), (0, CREME)):  # sombra 3D
        texto(ctx, s, x + d, y + d, 124, cor, "Poppins")
    # barra de XP em blocos
    by, bw, bh = y + 40, 520, 30
    passo = bw / total
    for i in range(total):
        arredondado(ctx, x + i * passo, by, passo - 4, bh, 4)
        ctx.set_source_rgb(*(TAUPE if i < n else CARTAO))
        ctx.fill()
    arredondado(ctx, x + (n - 1) * passo - 3, by - 3, passo + 2, bh + 6, 5)  # o de hoje brilha
    ctx.set_source_rgb(*CREME)
    ctx.set_line_width(3)
    ctx.stroke()
    texto(ctx, f"XP {n}/{total}", x + bw + 14, by + 25, 26, CREME)


def placa(ctx, s, x, y, ang):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(ang))
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(34)
    w = ctx.text_extents(s).x_advance + 130
    arredondado(ctx, 0, -32, w, 64, 14)
    ctx.set_source_rgb(*CREME)
    ctx.fill()
    ctx.arc(34, 0, 20, 0, 2 * math.pi)  # estrela de conquista num círculo
    ctx.set_source_rgb(*NAVY)
    ctx.fill()
    for k in range(10):
        r = 12 if k % 2 == 0 else 5
        a = -math.pi / 2 + k * math.pi / 5
        (ctx.line_to if k else ctx.move_to)(34 + r * math.cos(a), r * math.sin(a))
    ctx.close_path()
    ctx.set_source_rgb(*TAUPE)
    ctx.fill()
    texto(ctx, s, 66, 12, 34, NAVY)
    arredondado(ctx, w - 6, -20, 70, 40, 10)  # chip +XP
    ctx.set_source_rgb(*TAUPE)
    ctx.fill()
    texto(ctx, "+XP", w + 6, 9, 24, NAVY)
    ctx.restore()


def item(ctx, img, cx_f, cy_f, raio_f, x, y, R, rotulo):
    ih, iw = img.shape[:2]
    s, _ = superficie(img)
    halo = cairo.RadialGradient(x, y, R * 0.9, x, y, R * 1.6)
    halo.add_color_stop_rgba(0, *CREME, 0.55)
    halo.add_color_stop_rgba(1, *CREME, 0)
    ctx.arc(x, y, R * 1.6, 0, 2 * math.pi)
    ctx.set_source(halo)
    ctx.fill()
    ctx.arc(x, y, R + 10, 0, 2 * math.pi)
    ctx.set_source_rgb(*CREME)
    ctx.fill()
    ctx.save()
    ctx.arc(x, y, R, 0, 2 * math.pi)
    ctx.clip()
    k = R / (raio_f * iw)
    ctx.translate(x - cx_f * iw * k, y - cy_f * ih * k)
    ctx.scale(k, k)
    ctx.set_source_surface(s, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BEST)
    ctx.paint()
    ctx.restore()
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(24)
    w = ctx.text_extents(rotulo).x_advance + 30
    arredondado(ctx, x - w / 2, y + R - 6, w, 40, 20)
    ctx.set_source_rgb(*TAUPE)
    ctx.fill()
    texto(ctx, rotulo, x - w / 2 + 15, y + R + 22, 24, NAVY)


def montar(a):
    preparar()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    fundo(ctx)
    rosto = quadro(a.foto, None) if a.foto else quadro(a.fonte, a.rosto)
    cam = recorte(rosto, a.altura, a.contorno, a.cortar_esq, a.cortar_dir, a.remover_laranja)
    ps, _buf = argb(cam)
    ctx.set_source_surface(ps, W - cam.width + a.desloc[0], H - cam.height + a.desloc[1])
    ctx.paint()
    nivel(ctx, a.nivel, a.total, 56, 210, a.serie)
    for i, c in enumerate(a.conquistas):
        placa(ctx, c, 60 + i * 18, 360 + i * 92, -4 + i * 2.5)
    if a.item is not None:
        item(ctx, quadro(a.fonte, a.item), *a.item_centro, a.item_raio, W - 150, H - 150, 112, a.item_rotulo)
    nome = os.path.splitext(os.path.basename(a.fonte))[0]
    png = os.path.join(FINAL, f"{nome}_thumb.png")
    surf.write_to_png(png)
    jpg = png[:-4] + ".jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", jpg], check=True)
    print(f"pronto: {jpg} ({os.path.getsize(jpg) / 1e6:.1f} MB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--rosto", type=float, default=0.0)
    ap.add_argument("--foto")
    ap.add_argument("--nivel", type=int, required=True)
    ap.add_argument("--total", type=int, default=30)
    ap.add_argument("--conquistas", nargs="+", default=[])
    ap.add_argument("--item", type=float, help="s do quadro do item (ex.: o prato)")
    ap.add_argument("--item-centro", type=float, nargs=2, default=[0.5, 0.5])
    ap.add_argument("--item-raio", type=float, default=0.18, help="raio do item, em fração da largura do quadro")
    ap.add_argument("--item-rotulo", default="ITEM DO DIA")
    ap.add_argument("--altura", type=int, default=700)
    ap.add_argument("--cortar-esq", type=float, default=0.0, help="fração da largura da pessoa tirada da esquerda")
    ap.add_argument("--cortar-dir", type=float, default=0.0)
    ap.add_argument("--remover-laranja", action="store_true", help="tira do recorte objetos laranja/vermelhos do fundo")
    ap.add_argument("--serie", default="MELHORANDO MINHA VIDA EM 30 DIAS")
    ap.add_argument("--contorno", type=int, default=12)
    ap.add_argument("--desloc", type=int, nargs=2, default=[40, 30])
    montar(ap.parse_args())
