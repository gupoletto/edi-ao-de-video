#!/usr/bin/env python3
"""Exporta os cortes do plano para abrir no Premiere, DaVinci Resolve ou Final Cut e ajustar à mão.

    python3 edicao/ferramentas/exportar.py edicao/bruto/meu-video.mp4

Gera em edicao/trabalho/<nome>/:
- <nome>.edl          lista de cortes CMX3600 (abertura + trechos mantidos), importável nos três editores;
- <nome>_elementos.csv onde entra cada elemento (início/fim no vídeo editado + arquivo .mov), para arrastar
                       os clipes de elementos/ para uma faixa acima do vídeo.
"""
import csv
import os
import sys

from comum import ler, pasta_trabalho, sonda
from planejar import saida


def tc(seg, fps):
    q = int(round(seg * fps))
    f, s = q % round(fps), q // round(fps)
    return f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}:{f:02d}"


def exportar(fonte):
    pasta = pasta_trabalho(fonte)
    plano = ler(os.path.join(pasta, "plano.json"))
    fps = round(sonda(plano["fonte"])["fps"])
    nome = os.path.splitext(os.path.basename(plano["fonte"]))[0]
    linhas = [f"TITLE: {nome} editado", "FCM: NON-DROP FRAME", ""]
    rec = 0.0
    for k, (a, b) in enumerate(plano.get("abertura", []) + plano["manter"], 1):
        linhas.append(f"{k:03d}  AX       AA/V  C        {tc(a, fps)} {tc(b, fps)} {tc(rec, fps)} {tc(rec + b - a, fps)}")
        linhas.append(f"* FROM CLIP NAME: {os.path.basename(plano['fonte'])}")
        rec += b - a
    edl = os.path.join(pasta, f"{nome}.edl")
    with open(edl, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    els = os.path.join(pasta, f"{nome}_elementos.csv")
    with open(els, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n", "tipo", "inicio", "fim", "texto", "arquivo"])
        for i, e in enumerate(plano["elementos"], 1):
            w.writerow([i, e["tipo"], tc(saida(plano, e["de"]), fps), tc(saida(plano, e["ate"]), fps),
                        e.get("texto") or " · ".join(e.get("itens", [])), f"elementos/E{i:02d}_{e['tipo']}.mov"])
    print(f"{edl}\n{els}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    exportar(sys.argv[1])
