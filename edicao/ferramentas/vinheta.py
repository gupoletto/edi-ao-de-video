#!/usr/bin/env python3
"""Vinheta de fim (14 s): inscreva-se, like, comente, e espaço para a tela final do YouTube.

    python3 edicao/ferramentas/vinheta.py [--formato horizontal|vertical] [--serie "Melhorando minha vida em 30 dias"]
        -> edicao/estilo/vinheta_<formato>.mkv

0,0–7,5 s: interativa, na paleta do canal:
  - um cursor entra e clica em INSCREVER-SE, que vira INSCRITO com o sino tocando;
  - o like pula com +1 e confete;
  - um balão de comentário se escreve sozinho com a pergunta.
7,5–14 s: tela final. Ficam dois quadros vazios e um círculo, nos lugares onde se põem os elementos de tela final
no YouTube Studio (vídeo, vídeo, inscrever-se); no Studio, use o modelo "1 inscrição + 2 vídeos".
Som: trilha "pop" sintetizada e efeitos (clique, sino, pop, teclas), sem direitos autorais.
O montar.py emenda a vinheta no fim quando o plano tem "vinheta": true.
"""
import argparse
import math
import os
import subprocess
import tempfile

import cairo
import numpy as np
import soundfile as sf

import sons
from comum import ESTILO, preparar
from elementos import ESTILOS

FPS, DUR = 30, 14.0
FIM_INTERATIVA = 7.5


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mola(x):
    """0 -> 1 passando um pouco do ponto e voltando (pulo de botão)."""
    x = min(1.0, max(0.0, x))
    return 1 - math.cos(x * math.pi * 2.5) * math.exp(-x * 5)


def ret(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def fonte(ctx, tam, serif=False, italico=False):
    ctx.select_font_face("Source Serif 4" if serif else "Poppins",
                         cairo.FONT_SLANT_ITALIC if italico else cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(tam)


def centro(ctx, s, x, y, cor, a=1.0):
    e = ctx.text_extents(s)
    ctx.move_to(x - e.x_bearing - e.width / 2, y)
    ctx.set_source_rgba(*cor, a)
    ctx.show_text(s)


def cursor(ctx, x, y, s, cor_borda, cor):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(s, 1e-3), max(s, 1e-3))
    pts = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    ctx.set_source_rgb(*cor)
    ctx.fill_preserve()
    ctx.set_line_width(2.2)
    ctx.set_source_rgb(*cor_borda)
    ctx.stroke()
    ctx.restore()


def sino(ctx, x, y, r, cor, giro):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(giro)
    ctx.move_to(-r * 0.75, r * 0.45)
    ctx.curve_to(-r * 0.6, r * 0.2, -r * 0.65, -r * 0.7, 0, -r * 0.75)
    ctx.curve_to(r * 0.65, -r * 0.7, r * 0.6, r * 0.2, r * 0.75, r * 0.45)
    ctx.close_path()
    ctx.set_source_rgb(*cor)
    ctx.fill()
    ctx.arc(0, r * 0.62, r * 0.17, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def joinha(ctx, x, y, r, cor):
    """Mão de like: palma arredondada + polegar para cima."""
    ctx.save()
    ctx.translate(x, y)
    ret(ctx, -r * 0.55, -r * 0.15, r * 1.0, r * 0.85, r * 0.18)  # mão
    ctx.set_source_rgb(*cor)
    ctx.fill()
    ret(ctx, -r * 0.95, -r * 0.1, r * 0.3, r * 0.8, r * 0.08)  # punho/manga
    ctx.fill()
    ctx.move_to(-r * 0.45, -r * 0.1)  # polegar
    ctx.curve_to(-r * 0.3, -r * 0.5, -r * 0.1, -r * 0.75, -r * 0.05, -r * 0.95)
    ctx.curve_to(r * 0.0, -r * 1.12, r * 0.35, -r * 1.05, r * 0.25, -r * 0.7)
    ctx.line_to(r * 0.12, -r * 0.15)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def quadro(ctx, st, t, W, H, a):
    fundo, tinta, suave, destaque, cartao = (st[k] for k in ("fundo", "tinta", "suave", "destaque", "cartao"))
    vertical = H > W
    u = min(W, H) / 1080  # unidade: 1 px num quadro de 1080 de lado menor
    # fundo marinho entrando como uma onda de baixo para cima
    k = ease(t / 0.5)
    ctx.move_to(0, H)
    for i in range(41):
        x = W * i / 40
        ctx.line_to(x, H - H * 1.1 * k + math.sin(i * 0.5 + t * 6) * 30 * u * (1 - k))
    ctx.line_to(W, H)
    ctx.close_path()
    ctx.set_source_rgb(*fundo)
    ctx.fill()
    if t > 0.45:  # textura: pontinhos em grade que respiram
        for i in range(0, W, int(60 * u)):
            for j in range(0, H, int(60 * u)):
                ctx.new_sub_path()
                ctx.arc(i, j, 1.6 * u, 0, 2 * math.pi)
        ctx.set_source_rgba(*suave, 0.12)
        ctx.fill()
    if t < FIM_INTERATIVA + 0.6:
        sai = ease((t - FIM_INTERATIVA) / 0.5)
        ctx.save()
        ctx.translate(0, -H * 0.25 * sai)
        ctx.push_group()
        cx = W / 2
        # título
        fonte(ctx, 64 * u, serif=True, italico=True)
        centro(ctx, a.titulo, cx, H * (0.2 if not vertical else 0.22), tinta, ease((t - 0.4) / 0.4))
        # 1. inscrever-se
        bt = ease((t - 0.7) / 0.35)
        clique_t = 2.4
        inscrito = t >= clique_t
        aperto = 1 - 0.08 * math.exp(-((t - clique_t) / 0.06) ** 2)
        bw, bh = 520 * u, 112 * u
        by = H * (0.36 if not vertical else 0.36)
        ctx.save()
        ctx.translate(cx, by)
        s = mola((t - 0.7) / 0.6) * aperto
        ctx.scale(max(s, 1e-3), max(s, 1e-3))
        ret(ctx, -bw / 2, -bh / 2, bw, bh, bh / 2)
        ctx.set_source_rgb(*(cartao if inscrito else destaque))
        ctx.fill()
        fonte(ctx, 44 * u)
        if inscrito:
            centro(ctx, "INSCRITO", -22 * u, 16 * u, tinta)
            ctx.set_line_width(7 * u)  # visto desenhado
            ctx.set_source_rgb(*tinta)
            ctx.move_to(118 * u, 2 * u)
            ctx.line_to(134 * u, 18 * u)
            ctx.line_to(166 * u, -16 * u)
            ctx.stroke()
        else:
            centro(ctx, "INSCREVER-SE", 0, 16 * u, fundo)
        ctx.restore()
        if inscrito:  # sino aparece ao lado e balança
            sa = mola((t - clique_t - 0.1) / 0.5)
            giro = 0.5 * math.sin((t - clique_t) * 22) * math.exp(-(t - clique_t) * 2.5)
            sx = cx + bw / 2 + 95 * u
            ctx.save()
            ctx.translate(sx, by)
            ctx.scale(max(sa, 1e-3), max(sa, 1e-3))
            ctx.arc(0, 0, 56 * u, 0, 2 * math.pi)
            ctx.set_source_rgb(*tinta)
            ctx.fill()
            sino(ctx, 0, 0, 34 * u, fundo, giro)
            ctx.arc(26 * u, -26 * u, 11 * u, 0, 2 * math.pi)
            ctx.set_source_rgb(*destaque)
            ctx.fill()
            ctx.restore()
        # cursor vem de baixo à direita, clica e segue
        if 1.2 < t < 4.2:
            q = ease((t - 1.2) / 1.1)
            x0, y0 = cx + bw * 0.9, by + H * 0.4
            x1, y1 = cx + bw * 0.18, by + 6 * u
            if t > 3.2:
                q2 = ease((t - 3.2) / 0.8)
                x1, y1 = x1 + (cx + bw * 0.9 - x1) * q2, y1 + H * 0.2 * q2
            px, py = x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
            cursor(ctx, px, py, 2.4 * u * aperto, fundo, tinta)
            if abs(t - clique_t) < 0.25:  # onda do clique
                r = 30 * u + 220 * u * (t - clique_t + 0.25)
                ctx.arc(px, py, r, 0, 2 * math.pi)
                ctx.set_line_width(4 * u)
                ctx.set_source_rgba(*tinta, max(0.0, 0.6 - (t - clique_t + 0.25) * 1.2))
                ctx.stroke()
        # 2. like
        lt = 3.6
        if t > lt:
            ly = H * (0.56 if not vertical else 0.53)
            lx = cx - 160 * u
            s = mola((t - lt) / 0.6)
            ctx.save()
            ctx.translate(lx, ly)
            ctx.scale(max(s, 1e-3), max(s, 1e-3))
            ctx.arc(0, 0, 78 * u, 0, 2 * math.pi)
            ctx.set_source_rgb(*destaque)
            ctx.fill()
            joinha(ctx, 4 * u, 14 * u, 46 * u, fundo)
            ctx.restore()
            fonte(ctx, 46 * u)
            ctx.move_to(lx + 110 * u, ly + 16 * u)
            ctx.set_source_rgb(*tinta)
            ctx.show_text("DEIXA O LIKE")
            if t < lt + 1.2:  # +1 subindo e confete
                q = (t - lt) / 1.2
                fonte(ctx, 40 * u)
                centro(ctx, "+1", lx + 60 * u, ly - 90 * u - 80 * u * q, tinta, 1 - q)
                rnd = np.random.default_rng(4)
                for i in range(22):
                    ang = rnd.uniform(0, 2 * math.pi)
                    d = 260 * u * ease(q) * rnd.uniform(0.5, 1)
                    ctx.rectangle(lx + d * math.cos(ang), ly + d * math.sin(ang) + 120 * u * q * q, 10 * u, 6 * u)
                    ctx.set_source_rgba(*(tinta, destaque, suave)[i % 3], 1 - q)
                    ctx.fill()
        # 3. comentário que se escreve sozinho
        ct = 5.0
        if t > ct:
            cy_ = H * (0.75 if not vertical else 0.7)
            s = mola((t - ct) / 0.5)
            cw, ch = (1180 if not vertical else 900) * u, 150 * u
            ctx.save()
            ctx.translate(cx, cy_)
            ctx.scale(max(s, 1e-3), max(s, 1e-3))
            ret(ctx, -cw / 2, -ch / 2, cw, ch, 28 * u)
            ctx.move_to(-cw / 2 + 70 * u, ch / 2 - 1)
            ctx.line_to(-cw / 2 + 50 * u, ch / 2 + 40 * u)
            ctx.line_to(-cw / 2 + 120 * u, ch / 2 - 1)
            ctx.set_source_rgb(*tinta)
            ctx.fill()
            fonte(ctx, 30 * u)
            ctx.move_to(-cw / 2 + 40 * u, -ch / 2 + 46 * u)
            ctx.set_source_rgb(*suave)
            ctx.show_text("COMENTA AQUI")
            n = int(len(a.pergunta) * min(1.0, (t - ct - 0.3) / 1.6))
            fonte(ctx, (42 if not vertical else 36) * u)
            ctx.move_to(-cw / 2 + 40 * u, ch / 2 - 40 * u)
            ctx.set_source_rgb(*fundo)
            ctx.show_text(a.pergunta[:max(0, n)] + ("|" if int(t * 3) % 2 and n < len(a.pergunta) else ""))
            ctx.restore()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - sai)
        ctx.restore()
    if t > FIM_INTERATIVA:  # tela final: lugares dos elementos do YouTube
        q = ease((t - FIM_INTERATIVA - 0.2) / 0.5)
        fonte(ctx, 56 * u, serif=True, italico=True)
        centro(ctx, a.final, W / 2, H * 0.17 + (1 - q) * 40 * u, tinta, q)
        if a.serie:
            fonte(ctx, 28 * u)
            centro(ctx, a.serie.upper(), W / 2, H * 0.23 + (1 - q) * 40 * u, suave, q)
        if not vertical:
            caixas = [(W * 0.07, H * 0.32, W * 0.36, W * 0.36 * 9 / 16), (W * 0.57, H * 0.32, W * 0.36, W * 0.36 * 9 / 16)]
            circ = (W / 2, H * 0.82, H * 0.11)
        else:
            cw = W * 0.8
            caixas = [(W * 0.1, H * 0.3, cw, cw * 9 / 16), (W * 0.1, H * 0.3 + cw * 9 / 16 + H * 0.04, cw, cw * 9 / 16)]
            circ = (W / 2, H * 0.91, W * 0.1)
        for i, (x, y, w, h) in enumerate(caixas):
            qq = ease((t - FIM_INTERATIVA - 0.3 - i * 0.15) / 0.5)
            ctx.save()
            ctx.translate(x + w / 2, y + h / 2 + (1 - qq) * 60 * u)
            ret(ctx, -w / 2, -h / 2, w, h, 18 * u)
            ctx.set_source_rgba(*cartao, qq)
            ctx.fill_preserve()
            ctx.set_dash([14 * u, 10 * u])
            ctx.set_line_width(3 * u)
            ctx.set_source_rgba(*suave, 0.8 * qq)
            ctx.stroke()
            ctx.set_dash([])
            ctx.restore()
        cx_, cy_, r = circ
        qq = mola((t - FIM_INTERATIVA - 0.6) / 0.6)
        ctx.arc(cx_, cy_, r * max(qq, 0.0), 0, 2 * math.pi)
        ctx.set_source_rgb(*destaque)
        ctx.fill()


def audio(caminho):
    n = int(DUR * sons.SR)
    mix = sons.trilha("pop", DUR, inicio_suave=0.3, fim_suave=2.0) * 0.9

    def por(som, t, g=1.0):
        i = int(t * sons.SR)
        s = som[:n - i] * g
        mix[i:i + len(s)] += s[:, None]

    por(sons.whoosh(0.5), 0.0)
    por(sons.clique(), 2.4, 1.2)
    por(sons.ding(), 2.55, 0.8)
    por(sons.pop(), 3.6, 1.2)
    for k in range(26):  # teclas do comentário
        por(sons.clique(), 5.3 + k * 0.062, 0.35)
    por(sons.whoosh(0.5), FIM_INTERATIVA - 0.1)
    por(sons.pop(), FIM_INTERATIVA + 0.6)
    m = np.abs(mix).max()
    sf.write(caminho, mix / m * 0.7, sons.SR)


def gerar(a):
    preparar()
    st = ESTILOS["editorial"]
    W, H = (1920, 1080) if a.formato == "horizontal" else (1080, 1920)
    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, "a.wav")
    audio(wav)
    out = os.path.join(ESTILO, f"vinheta_{a.formato}.mkv")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "12",
                            "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-colorspace", "bt709", "-c:a", "pcm_s16le", "-ar", "48000", "-shortest", out],
                           stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    for f in range(int(DUR * FPS)):
        ctx.set_source_rgb(*(st["tinta"] if f / FPS < 0.6 else st["fundo"]))  # a onda marinho sobe sobre o creme
        ctx.paint()
        quadro(ctx, st, f / FPS, W, H, a)
        surf.flush()
        enc.stdin.write(bytes(surf.get_data()))
    enc.stdin.close()
    enc.wait()
    print(f"pronto: {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--formato", default="horizontal", choices=["horizontal", "vertical"])
    ap.add_argument("--titulo", default="Curtiu o vídeo?")
    ap.add_argument("--pergunta", default="O que você quer ver nos próximos vídeos?")
    ap.add_argument("--final", default="Assiste o próximo!")
    ap.add_argument("--serie", default="Melhorando minha vida em 30 dias")
    gerar(ap.parse_args())
