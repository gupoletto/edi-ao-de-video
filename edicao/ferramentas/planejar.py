#!/usr/bin/env python3
"""Etapa 3: monta o plano de edição a partir da transcrição.

    python3 edicao/ferramentas/planejar.py edicao/bruto/meu-video.mp4 [--estilo editorial|dinamico]
                                           [--formato horizontal|vertical] [--ritmo normal|rapido]

Faz a parte mecânica, medida nos vídeos de referência (fala em 89–97 % do tempo, pausas de ~0,27 s):
- corta pausas maiores que 0,35 s (--ritmo rapido: 0,25 s, como nos tutoriais mais rápidos), deixando 0,1 s de respiro de cada lado (nunca no meio de palavra:
  os cortes caem nos silêncios que o detector de voz encontrou);
- marca regravações (frase repetida logo em seguida) e fica com a última tomada;
- alterna um zoom leve (110 %) a cada corte seco, para o corte não "pular".
Os elementos visuais (letreiros, títulos, listas, números) ficam em "elementos": quem preenche é o
Claude, lendo a transcrição e o guia edicao/ESTILO.md. Saída: trabalho/<nome>/plano.json e plano.md.
"""
import argparse
import difflib
import os
import re

from comum import gravar, hms, ler, pasta_trabalho

RESPIRO = 0.10  # s de silêncio mantidos antes de cada frase
RESPIRO_FIM = 0.16  # e depois: o fim da última sílaba é fraco e o detector de voz o corta cedo
ZOOM = 1.10


def norm(t):
    return re.sub(r"[^\wà-ú ]", "", t.lower()).split()


def regravacoes(segs):
    """Índices de frases que parecem uma tomada descartada (a seguinte recomeça igual)."""
    fora = set()
    for i in range(len(segs) - 1):
        a, b = norm(segs[i]["text"]), norm(segs[i + 1]["text"])
        if len(a) < 3 or len(b) < 3:
            continue
        inicio_igual = a[:4] == b[:4]
        parecido = difflib.SequenceMatcher(None, a, b[:len(a) + 3]).ratio() > 0.72
        if inicio_igual or parecido:
            fora.add(i)
    return fora


def planejar(fonte, estilo="editorial", formato="horizontal", pausa=0.35):
    """Recalcula cortes e zooms. Apaga os elementos e a abertura de um plano anterior."""
    pasta = pasta_trabalho(fonte)
    tr = ler(os.path.join(pasta, "transcricao.json"))
    segs = tr["segments"]
    fora = regravacoes(segs)
    sugestoes = [{"de": segs[i]["start"], "ate": segs[i]["end"], "motivo": "regravação", "texto": segs[i]["text"]}
                 for i in sorted(fora)]
    # intervalos mantidos: frases + respiro, unindo as que ficam a menos de `pausa`
    manter = []
    for i, s in enumerate(segs):
        if i in fora:
            continue
        a, b = max(0.0, s["start"] - RESPIRO), min(tr["dur"], s["end"] + RESPIRO_FIM)
        if manter and a - manter[-1][1] < pausa - RESPIRO - RESPIRO_FIM:
            manter[-1][1] = b
        else:
            if manter:
                sugestoes.append({"de": manter[-1][1], "ate": a, "motivo": f"pausa de {a - manter[-1][1]:.1f} s"})
            manter.append([a, b])
    zooms = [{"de": a, "ate": b, "escala": ZOOM} for k, (a, b) in enumerate(manter) if k % 2 == 1]
    plano = {
        "fonte": tr["fonte"], "estilo": estilo, "formato": formato,
        "foco": [0.5, 0.42],  # ponto do rosto (fração da largura, da altura) usado no zoom e no corte vertical
        "legendas": formato == "vertical" or estilo == "dinamico",
        "legenda_estilo": "palavra" if estilo == "dinamico" else "frase",  # palavra | frase | caixa
        "sons": True,  # efeitos sonoros sintetizados na entrada dos elementos
        "abertura": [],  # gancho: trechos do bruto [[de, ate], ...] mostrados antes de tudo
        "manter": [[round(a, 3), round(b, 3)] for a, b in manter],
        "cortes": sorted(sugestoes, key=lambda c: c["de"]),
        "zooms": zooms,
        "correcoes": {},  # palavras que a transcrição erra, para as legendas (ex.: {"cloud": "Claude"})
        "elementos": [],
    }
    gravar(os.path.join(pasta, "plano.json"), plano)
    escrever_md(pasta, plano, tr)
    dur_out = sum(b - a for a, b in manter)
    print(f"plano: {len(manter)} trechos, {tr['dur']:.0f}s -> {dur_out:.0f}s "
          f"({len([c for c in sugestoes if c['motivo'] == 'regravação'])} regravações) -> {pasta}/plano.md")
    return plano


def dur_abertura(plano):
    return sum(b - a for a, b in plano.get("abertura", []))


def saida(plano, t):
    """Tempo na fonte -> tempo no vídeo editado (a abertura, se houver, vem antes)."""
    acc = dur_abertura(plano)
    for a, b in plano["manter"]:
        if t < a:
            return acc
        if t <= b:
            return acc + t - a
        acc += b - a
    return acc


def escrever_md(pasta, plano, tr):
    L = [f"# Plano de edição — {os.path.basename(plano['fonte'])}", "",
         f"Estilo **{plano['estilo']}**, formato **{plano['formato']}**, legendas "
         f"{'sim' if plano['legendas'] else 'não'}. Tempos no formato mm:ss do vídeo **editado** "
         "(entre parênteses, o tempo no bruto).", "", "## Elementos visuais", ""]
    if not plano["elementos"]:
        L.append("_(ainda vazio: o Claude preenche lendo a transcrição e o ESTILO.md)_")
    for i, e in enumerate(plano["elementos"], 1):
        txt = e.get("texto") or " · ".join(e.get("itens", []))
        L.append(f"{i}. **{hms(saida(plano, e['de']))}–{hms(saida(plano, e['ate']))}** {e['tipo']}: {txt}"
                 f"  ({hms(e['de'])})")
    if plano.get("abertura"):
        L += ["", "## Abertura (gancho)", ""] + [f"- {hms(a)}–{hms(b)} do bruto" for a, b in plano["abertura"]]
    L += ["", "## Cortes", ""]
    for c in plano["cortes"]:
        extra = f" — “{c['texto']}”" if c.get("texto") else ""
        L.append(f"- {hms(c['de'])}–{hms(c['ate'])} (bruto): {c['motivo']}{extra}")
    L += ["", f"## Zoom no rosto: {len(plano['zooms'])} trechos a {ZOOM:.0%}, alternando a cada corte", ""]
    with open(os.path.join(pasta, "plano.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--estilo", default="editorial", choices=["editorial", "dinamico"])
    ap.add_argument("--formato", default="horizontal", choices=["horizontal", "vertical"])
    ap.add_argument("--ritmo", default="normal", choices=["normal", "rapido"])
    a = ap.parse_args()
    planejar(a.fonte, a.estilo, a.formato, 0.25 if a.ritmo == "rapido" else 0.35)
