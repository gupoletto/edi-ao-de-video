#!/usr/bin/env python3
"""Etapa 4: renderiza cada elemento do plano como um clipe curto (.mov com transparência).

    python3 edicao/ferramentas/elementos.py edicao/bruto/meu-video.mp4 [--amostra]

--amostra gera só um quadro PNG de cada elemento (para revisar antes de renderizar tudo).

Tipos (campos em plano.json -> "elementos"; "de"/"ate" em segundos do vídeo BRUTO):
  titulo   tela cheia: "texto", "destaque" (palavra em cor), "rotulo" opcional (ex.: "PASSO 2 DE 5")
  lista    tela cheia: "texto" (título), "itens" [..], "marca": "check" | "x" | "numero",
           "tempos" opcional [..] (instante no bruto em que cada item entra)
  letreiro sobre o rosto: "itens" [..] em pílulas que entram uma a uma, "lado": "esquerda" | "direita"
  numero   tela cheia: "texto" (o número, ex.: "R$ 12 mil"), "legenda", "contar_de" opcional (conta até o número)
  sumario  tela cheia: "texto" (título), "itens" [etapas], "atual" (índice da etapa que começa agora)
  dividido rosto num cartão + texto ao lado: "texto", "destaque", "itens" opcional, "lado": "esquerda" | "direita"
Em "itens" do letreiro, "~texto~" sai riscado (ex.: "~Premiere~").
Feitos direto no montar.py, com o próprio vídeo (sem clipe):
  tela     gravação de tela em tela cheia + rosto em miniatura: "arquivo" (ex.: "bruto/tela.mp4"), "inicio" (s no
           arquivo), "pip": "esquerda" | "direita"
  foco     holofote: escurece fora de "area" [x, y, w, h] (frações da tela)
  popup    recorta "area" [x, y, w, h] e mostra ampliada ("escala", padrão 1.6)
"""
import argparse
import math
import os
import re
import subprocess

import cairo
import numpy as np

from comum import ler, pasta_trabalho, preparar
from planejar import saida

FPS = 30
def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


# Paleta do canal (28/10/2026): marinho #01103A, creme #F8EDD9, cinza-azulado #919FA8, taupe #B19F92.
# Fundo marinho com texto creme, como na referência; taupe e cinza-azulado têm contraste sobre o marinho
# (não sobre o creme), por isso são destaque e cor secundária, e nunca texto em fundo claro.
MARINHO, CREME, CINZA, TAUPE = "#01103A", "#F8EDD9", "#919FA8", "#B19F92"
PALETA = {
    "fundo": hexrgb(MARINHO), "tinta": hexrgb(CREME), "suave": hexrgb(CINZA), "destaque": hexrgb(TAUPE),
    "ok": hexrgb(CINZA), "nao": hexrgb(TAUPE), "cartao": hexrgb("#0E2152"),  # marinho um tom acima, p/ cartões
}
ESTILOS = {
    "editorial": dict(PALETA, titulo=("Source Serif 4 Semibold", False), corpo=("Inter", True)),  # Marcos Lemos
    "dinamico": dict(PALETA, titulo=("Poppins ExtraBold", False), corpo=("Poppins SemiBold", False)),  # Matheus F.
}


def fonte(ctx, familia, negrito, tam):
    ctx.select_font_face(familia, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if negrito else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(tam)


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def quebrar(ctx, palavras, largura):
    linhas, cur = [], []
    for w in palavras:
        if cur and ctx.text_extents(" ".join(cur + [w])).x_advance > largura:
            linhas.append(cur)
            cur = [w]
        else:
            cur.append(w)
    return linhas + ([cur] if cur else [])


def titulo_com_destaque(ctx, st, texto, destaque, x, y, tam, largura, centro=False):
    """Título que quebra linha; as palavras do destaque saem na cor de destaque. Retorna o y final."""
    fam, neg = st["titulo"]
    fonte(ctx, fam, neg, tam)
    alvo = set(norm(destaque or ""))
    linhas = quebrar(ctx, texto.split(), largura)
    for ln in linhas:
        frase = " ".join(ln)
        xx = x - ctx.text_extents(frase).x_advance / 2 if centro else x
        for w in ln:
            ctx.set_source_rgb(*(st["destaque"] if norm(w) and set(norm(w)) <= alvo else st["tinta"]))
            ctx.move_to(xx, y)
            ctx.show_text(w)
            xx += ctx.text_extents(w + " ").x_advance
        y += tam * 1.18
    return y


def norm(t):
    return [p for p in "".join(c if c.isalnum() or c == " " else " " for c in t.lower()).split()]


def icone(ctx, st, marca, x, y, r, n):
    if marca == "numero":
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgb(*st["destaque"])
        ctx.fill()
        fonte(ctx, *st["corpo"], r * 1.1)
        s = str(n)
        e = ctx.text_extents(s)
        ctx.set_source_rgb(*st["fundo"])
        ctx.move_to(x - e.x_bearing - e.width / 2, y - e.y_bearing - e.height / 2)
        ctx.show_text(s)
        return
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source_rgb(*(st["ok"] if marca == "check" else st["nao"]))
    ctx.fill()
    ctx.set_source_rgb(*st["fundo"])
    ctx.set_line_width(r * 0.28)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if marca == "check":
        ctx.move_to(x - r * 0.45, y)
        ctx.line_to(x - r * 0.1, y + r * 0.38)
        ctx.line_to(x + r * 0.5, y - r * 0.35)
    else:
        for s in (1, -1):
            ctx.move_to(x - r * 0.38, y - s * r * 0.38)
            ctx.line_to(x + r * 0.38, y + s * r * 0.38)
    ctx.stroke()


# ---------- tipos ----------

def d_titulo(ctx, st, e, t, W, H):
    ctx.set_source_rgb(*st["fundo"])
    ctx.paint()
    k = ease(t / 0.5)
    ctx.translate(0, 24 * (1 - k))
    tam = H * (0.085 if W > H else 0.055)
    y = H * 0.44
    if e.get("rotulo"):
        fonte(ctx, *st["corpo"], tam * 0.32)
        s = e["rotulo"].upper()
        ctx.set_source_rgba(*st["destaque"], k)
        ctx.move_to(W / 2 - ctx.text_extents(s).x_advance / 2, y - tam * 1.1)
        ctx.show_text(s)
    ctx.push_group()
    y2 = titulo_com_destaque(ctx, st, e["texto"], e.get("destaque"), W / 2, y, tam, W * 0.8, centro=True)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(k)
    if e.get("rotulo"):  # o traço curto sob o título, como nos cards "PASSO 2 DE 5"
        ctx.set_source_rgba(*st["destaque"], k)
        ctx.rectangle(W / 2 - 60 * k, y2 - tam * 0.55, 120 * k, 5)
        ctx.fill()


def d_lista(ctx, st, e, t, W, H):
    ctx.set_source_rgb(*st["fundo"])
    ctx.paint()
    itens, marca = e.get("itens", []), e.get("marca", "check")
    dur = e["ate"] - e["de"]
    tam = H * (0.062 if W > H else 0.042)
    x0 = W * (0.12 if W > H else 0.09)
    y = titulo_com_destaque(ctx, st, e.get("texto", ""), e.get("destaque"), x0, H * 0.2, tam, W * 0.76)
    passo = max(0.35, min(1.2, (dur * 0.6) / max(1, len(itens))))
    fam, neg = st["corpo"]
    ti = tam * 0.62
    y += ti * 0.8
    tempos = e.get("tempos")  # opcional: instante (no bruto) em que cada item é falado
    for i, it in enumerate(itens):
        ini = tempos[i] - e["de"] if tempos else 0.4 + i * passo
        k = ease((t - ini) / 0.35)
        if k <= 0:
            break
        ctx.save()
        ctx.translate(30 * (1 - k), 0)
        ctx.push_group()
        h = ti * 2.1
        rr(ctx, x0, y, W - 2 * x0, h, 16)
        ctx.set_source_rgb(*st["cartao"])
        ctx.fill()
        icone(ctx, st, marca, x0 + h * 0.5, y + h / 2, ti * 0.55, i + 1)
        fonte(ctx, fam, neg, ti)
        ctx.set_source_rgb(*st["tinta"])
        ctx.move_to(x0 + h * 1.05, y + h / 2 + ti * 0.36)
        ctx.show_text(it)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(k)
        ctx.restore()
        y += h + ti * 0.55


def d_letreiro(ctx, st, e, t, W, H):
    itens = e.get("itens", [])
    dur = e["ate"] - e["de"]
    passo = max(0.3, min(1.0, (dur * 0.5) / max(1, len(itens))))
    tam = H * (0.03 if W > H else 0.022)
    fam, neg = st["corpo"]
    fonte(ctx, fam, neg, tam)
    y = H * 0.06
    for i, it in enumerate(itens):
        k = ease((t - 0.15 - i * passo) / 0.3)
        if k <= 0:
            break
        w = ctx.text_extents(it.strip("~")).x_advance + tam * 2.6
        h = tam * 2.0
        x = W * 0.03 if e.get("lado", "esquerda") == "esquerda" else W * 0.97 - w
        ctx.save()
        ctx.translate(-20 * (1 - k), 0)
        ctx.push_group()
        rr(ctx, x + 3, y + 5, w, h, 12)
        ctx.set_source_rgba(0, 0, 0, 0.18)
        ctx.fill()
        rr(ctx, x, y, w, h, 12)
        ctx.set_source_rgb(*st["cartao"])
        ctx.fill()
        ctx.arc(x + tam * 1.0, y + h / 2, tam * 0.28, 0, 2 * math.pi)
        ctx.set_source_rgb(*st["destaque"])
        ctx.fill()
        riscado = it.startswith("~") and it.endswith("~")
        txt = it.strip("~")
        ctx.set_source_rgb(*(st["suave"] if riscado else st["tinta"]))
        fonte(ctx, fam, neg, tam)
        ctx.move_to(x + tam * 1.8, y + h / 2 + tam * 0.36)
        ctx.show_text(txt)
        if riscado:  # o traço atravessa a palavra logo depois que ela entra
            r = ease((t - 0.15 - i * passo - 0.35) / 0.3)
            ctx.set_source_rgb(*st["nao"])
            ctx.set_line_width(tam * 0.12)
            ctx.move_to(x + tam * 1.6, y + h / 2)
            ctx.line_to(x + tam * 1.6 + (ctx.text_extents(txt).x_advance + tam * 0.4) * r, y + h / 2)
            ctx.stroke()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(k)
        ctx.restore()
        y += h + tam * 0.6


def d_numero(ctx, st, e, t, W, H):
    ctx.set_source_rgb(*st["fundo"])
    ctx.paint()
    k = ease(t / 0.6)
    tam = H * (0.2 if W > H else 0.11)
    fam, neg = st["titulo"]
    fonte(ctx, fam, neg, tam)
    s = e["texto"]
    if "contar_de" in e:
        s = contando(s, e["contar_de"], ease(t / 1.4))
    ctx.set_source_rgba(*st["destaque"], k)
    ctx.move_to(W / 2 - ctx.text_extents(s).x_advance / 2, H * 0.52 + 20 * (1 - k))
    ctx.show_text(s)
    if e.get("legenda"):
        fonte(ctx, *st["corpo"], tam * 0.22)
        ctx.set_source_rgba(*st["suave"], ease((t - 0.3) / 0.5))
        s = e["legenda"]
        ctx.move_to(W / 2 - ctx.text_extents(s).x_advance / 2, H * 0.52 + tam * 0.5)
        ctx.show_text(s)


def contando(texto, de, k):
    """'R$ 12.500' contando a partir de `de`: troca só o número, mantém prefixo, sufixo e separadores."""
    m = re.search(r"\d[\d.]*(,\d+)?", texto)
    if not m:
        return texto
    bruto = m.group(0)
    dec = len(bruto.split(",")[1]) if "," in bruto else 0
    alvo = float(bruto.replace(".", "").replace(",", "."))
    v = de + (alvo - de) * k
    num = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return texto[:m.start()] + num + texto[m.end():]


def d_sumario(ctx, st, e, t, W, H):
    """Mapa do vídeo com a etapa atual em destaque (as anteriores marcadas, as próximas apagadas)."""
    ctx.set_source_rgb(*st["fundo"])
    ctx.paint()
    itens, atual = e.get("itens", []), e.get("atual", 0)
    tam = H * (0.05 if W > H else 0.034)
    x0 = W * (0.3 if W > H else 0.12)
    y = H * 0.5 - (len(itens) - 1) * tam * 0.85 + tam * 0.35  # bloco centrado na tela
    if e.get("texto"):
        fonte(ctx, *st["corpo"], tam * 0.5)
        ctx.set_source_rgb(*st["destaque"])
        ctx.move_to(x0, y - tam * 1.4)
        ctx.show_text(e["texto"].upper())
    k = ease((t - 0.3) / 0.5)
    for i, it in enumerate(itens):
        fam, neg = st["titulo"] if i == atual else st["corpo"]
        fonte(ctx, fam, neg, tam * (1 + 0.18 * k if i == atual else 0.8))
        if i < atual:
            ctx.set_source_rgba(*st["suave"], 0.55)
        elif i == atual:
            ctx.set_source_rgb(*st["tinta"])
        else:
            ctx.set_source_rgba(*st["suave"], 0.35)
        ctx.move_to(x0 + (tam * 0.9 * k if i == atual else 0), y)
        ctx.show_text(it)
        if i == atual:
            ctx.set_source_rgba(*st["destaque"], k)
            ctx.move_to(x0 - tam * 0.4, y)
            ctx.show_text("→")
        elif i < atual:
            icone(ctx, st, "check", x0 - tam * 0.55, y - tam * 0.3, tam * 0.28, 0)
        y += tam * 1.7


def cartao_rect(W, H, lado="esquerda"):
    """Onde fica o rosto na tela dividida (x, y, w, h). O montar.py coloca o vídeo exatamente aqui."""
    if W > H:
        w, h = W * 0.30, H * 0.74
        x = W * 0.07 if lado == "esquerda" else W * 0.93 - w
        return x, (H - h) / 2, w, h
    w, h = W * 0.78, H * 0.42
    return (W - w) / 2, H * 0.09, w, h


def d_dividido(ctx, st, e, t, W, H):
    ctx.set_source_rgb(*st["fundo"])
    ctx.paint()
    x, y, w, h = cartao_rect(W, H, e.get("lado", "esquerda"))
    for k in range(6):  # sombra macia em volta do cartão
        rr(ctx, x - k * 3, y - k * 3 + 10, w + k * 6, h + k * 6, 28 + k * 3)
        ctx.set_source_rgba(0, 0, 0, 0.025)
        ctx.fill()
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_CLEAR)  # buraco: o vídeo aparece por baixo
    rr(ctx, x, y, w, h, 28)
    ctx.fill()
    ctx.restore()
    if W > H:
        tx = x + w + W * 0.06 if e.get("lado", "esquerda") == "esquerda" else W * 0.07
        larg, ty, tam = W * 0.5, H * 0.38, H * 0.075
    else:
        tx, larg, ty, tam = W * 0.1, W * 0.8, y + h + H * 0.1, H * 0.045
    k = ease((t - 0.2) / 0.5)
    ctx.push_group()
    yy = titulo_com_destaque(ctx, st, e.get("texto", ""), e.get("destaque"), tx, ty, tam, larg)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(k)
    fam, neg = st["corpo"]
    ti = tam * 0.5
    yy += ti
    for i, it in enumerate(e.get("itens", [])):
        a = ease((t - 0.8 - i * 0.6) / 0.35)
        if a <= 0:
            break
        fonte(ctx, fam, neg, ti)
        ctx.set_source_rgba(*st["tinta"], a)
        ctx.move_to(tx + 20 * (1 - a), yy)
        ctx.show_text("· " + it)
        yy += ti * 1.7


TIPOS = {"titulo": d_titulo, "lista": d_lista, "letreiro": d_letreiro, "numero": d_numero,
         "sumario": d_sumario, "dividido": d_dividido}
TELA_CHEIA = {"titulo", "lista", "numero", "sumario", "dividido"}
SO_MONTAR = {"tela", "foco", "popup"}  # não geram clipe: o montar.py faz com o próprio vídeo
FADE = 0.25


def quadro(st, e, t, W, H):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.push_group()
    TIPOS[e["tipo"]](ctx, st, e, t, W, H)
    ctx.pop_group_to_source()
    dur = e["ate"] - e["de"]
    ctx.paint_with_alpha(min(1.0, t / FADE, (dur - t) / FADE) if e["tipo"] in TELA_CHEIA else min(1.0, (dur - t) / FADE))
    surf.flush()
    return surf


def no_editado(plano, e):
    """Elemento com os tempos convertidos para o vídeo editado (os cortes encolhem a duração)."""
    e = dict(e, de=saida(plano, e["de"]), ate=saida(plano, e["ate"]))
    if e.get("tempos"):
        e["tempos"] = [saida(plano, t) for t in e["tempos"]]
    return e


def resolucao(plano):
    return (1080, 1920) if plano["formato"] == "vertical" else (1920, 1080)


def renderizar(fonte_video, amostra=False):
    preparar()
    pasta = pasta_trabalho(fonte_video)
    plano = ler(os.path.join(pasta, "plano.json"))
    st = ESTILOS[plano["estilo"]]
    W, H = resolucao(plano)
    out_dir = os.path.join(pasta, "elementos")
    os.makedirs(out_dir, exist_ok=True)
    for i, e in enumerate(plano["elementos"], 1):
        if e["tipo"] in SO_MONTAR:
            continue
        e = no_editado(plano, e)
        nome = f"E{i:02d}_{e['tipo']}"
        dur = e["ate"] - e["de"]
        if amostra:
            quadro(st, e, min(dur * 0.8, 2.5), W, H).write_to_png(os.path.join(out_dir, nome + ".png"))
            continue
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "qtrle", os.path.join(out_dir, nome + ".mov")],
                               stdin=subprocess.PIPE)
        for f in range(int(math.ceil(dur * FPS))):
            s = quadro(st, e, f / FPS, W, H)
            px = np.frombuffer(s.get_data(), np.uint8).reshape(H, W, 4).astype(np.float32)
            a = px[..., 3:4]
            px[..., :3] = np.where(a > 0, px[..., :3] * 255 / np.maximum(a, 1), 0)  # cairo é pré-multiplicado
            enc.stdin.write(px.clip(0, 255).astype(np.uint8).tobytes())
        enc.stdin.close()
        enc.wait()
        print(f"  {nome}: {dur:.1f}s")
    print(f"{len(plano['elementos'])} elementos -> {out_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--amostra", action="store_true")
    a = ap.parse_args()
    renderizar(a.fonte, a.amostra)
