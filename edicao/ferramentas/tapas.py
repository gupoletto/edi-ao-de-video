#!/usr/bin/env python3
"""Tapa na câmera = fim do take. Acha os tapas e as emendas entre clipes, e tira o que não é para aparecer.

    python3 edicao/ferramentas/tapas.py edicao/bruto/meu-video.mkv     # lista o que achou

Combinado com o usuário: quando ele dá um tapa (ou soco) na câmera, o corte acaba ali. Tudo o que vem depois
(a câmera balançando, a camiseta, o chão) sai, até o próximo clipe começar.

- Tapa: a mão cobre a lente (quadro quase liso: nitidez < 30 % da mediana do vídeo por 2+ quadros) junto de uma
  pancada no áudio (pico > 3x a mediana, até 0,3 s antes ou durante), ou a mão que tapa a lente e o clipe acaba
  logo depois (até 0,3 s), mesmo sem barulho. Corta 0,2 s antes da lente cobrir, que é quando a mão já entra.
- Emenda: um salto de imagem num quadro só (o bruto vem de vários clipes do celular colados). Um trecho mantido
  que entra menos de 0,6 s num clipe vizinho perde esse pedaço: são restos (a cama, o chão, a mão ligando a
  câmera), nunca conteúdo.
- Câmera virando (o pé, o chão, a camiseta no começo ou no fim do take): num clipe em que o rosto aparece na maior
  parte do tempo, as pontas sem rosto (até 4 s) saem. O rosto é achado pelo YuNet (OpenCV, modelo de 230 kB do
  opencv_zoo); clipes quase sem rosto (bike, show, paisagem) ficam inteiros.
Resultado em cache em trabalho/<nome>/tapas.json; planejar.py e montar.py aplicam sozinhos.
"""
import os
import subprocess
import sys

import numpy as np

from comum import gravar, hms, ler, pasta_trabalho, sonda

YUNET = "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
ANTES = 0.20  # s cortados antes da lente cobrir (a mão já aparece)
RESTO = 0.60  # s: menos que isso dentro de outro clipe é resto


def sinais(fonte):
    """Por quadro: pico do áudio, movimento (diferença entre quadros) e nitidez, numa versão 64x36 cinza."""
    fps = round(sonda(fonte)["fps"])
    sr = 16000
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", fonte, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    w = sr // fps
    pico = np.abs(a[:len(a) // w * w].reshape(-1, w)).max(1)
    W, H = 64, 36
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", fonte, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo",
                          "-"], capture_output=True, check=True).stdout
    v = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    mov = np.r_[0, np.abs(np.diff(v, axis=0)).mean((1, 2))]
    nit = np.abs(np.diff(v, axis=2)).mean((1, 2))
    n = min(len(pico), len(mov))
    return fps, pico[:n], mov[:n], nit[:n]


def rostos(fonte, passo=0.2):
    """Tempos (s) e se há rosto em cada um, olhando 5 quadros por segundo em 320x180."""
    import urllib.request
    import cv2
    modelo = os.path.expanduser("~/.cache/rosto/yunet.onnx")
    if not os.path.exists(modelo):
        os.makedirs(os.path.dirname(modelo), exist_ok=True)
        urllib.request.urlretrieve(YUNET, modelo)
    w, h = 320, 180
    det = cv2.FaceDetectorYN.create(modelo, "", (w, h), 0.6)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", fonte, "-vf", f"fps={1 / passo},scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    quadros = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    tem = np.array([det.detect(np.ascontiguousarray(q))[1] is not None for q in quadros])
    return np.arange(len(tem)) * passo, tem


def bordas_sem_rosto(fonte, emendas, fim, maximo=4.0):
    t, tem = rostos(fonte)
    out = []
    limites = [0.0] + list(emendas) + [fim]
    for a, b in zip(limites, limites[1:]):
        dentro = (t >= a) & (t < b)
        if b - a < 1.5 or dentro.sum() < 5 or tem[dentro].mean() < 0.5:
            continue  # clipe curto ou de cena (sem você): fica inteiro
        ts, ok = t[dentro], tem[dentro]
        firme = [i for i in range(len(ok) - 2) if ok[i] and ok[i + 1] and ok[i + 2]]
        if not firme:
            continue
        ini, fim_r = ts[firme[0]], ts[firme[-1] + 2]
        if 0.25 < ini - a <= maximo:
            out.append([round(a, 3), round(ini - 0.1, 3)])
        if 0.4 < b - fim_r <= maximo:
            out.append([round(fim_r + 0.2, 3), round(b, 3)])
    return out


def detectar(fonte, refazer=False):
    cache = os.path.join(pasta_trabalho(fonte), "tapas.json")
    if os.path.exists(cache) and not refazer:
        return ler(cache)
    fps, pico, mov, nit = sinais(fonte)
    emendas = []
    lim = max(25.0, 6 * float(np.median(mov)))
    for i in range(2, len(mov) - 2):
        viz = max(mov[i - 2], mov[i - 1], mov[i + 1], mov[i + 2])
        if mov[i] > lim and mov[i] > 2.5 * viz:
            emendas.append(round(i / fps, 3))
    tapas = []
    coberto = nit < 0.3 * float(np.median(nit))
    pmed = float(np.median(pico))
    i = 0
    while i < len(coberto):
        if coberto[i] and i + 1 < len(coberto) and coberto[i + 1]:
            j = i
            while j < len(coberto) and coberto[j]:
                j += 1
            janela = pico[max(0, i - int(0.3 * fps)):j + 3]
            fim_de_clipe = any(0 <= e - j / fps <= 0.3 for e in emendas)
            if janela.max() > 3 * pmed or fim_de_clipe:
                t = i / fps
                depois = [e for e in emendas if e >= (j - 1) / fps]  # o clipe seguinte, depois da mão sair
                tapas.append({"tapa": round(max(0.0, t - ANTES), 3), "retoma": depois[0] if depois else None})
            i = j
        i += 1
    info = {"tapas": tapas, "emendas": emendas,
            "bordas": bordas_sem_rosto(fonte, emendas, len(mov) / fps)}
    gravar(cache, info)
    return info


def aplicar(intervalos, info, fim):
    """Tira dos intervalos [a, b] o que vem depois de cada tapa (até a próxima emenda, ou o fim do bruto)
    e as pontas de menos de RESTO s que atravessam uma emenda. Devolve (intervalos, [(de, ate, motivo)])."""
    fora = [(t["tapa"], t["retoma"] if t["retoma"] is not None else fim, "tapa na câmera") for t in info["tapas"]]
    fora += [(x, y, "câmera virando, sem rosto") for x, y in info.get("bordas", [])]
    out, removido = [], []
    for a, b in intervalos:
        pedacos = [[a, b]]
        for x, y, motivo in fora:
            novos = []
            for p, q in pedacos:
                if y <= p or x >= q:
                    novos.append([p, q])
                    continue
                removido.append((max(p, x), min(q, y), motivo))
                if x > p:
                    novos.append([p, x])
                if y < q:
                    novos.append([y, q])
            pedacos = novos
        for p, q in pedacos:
            for e in info["emendas"]:
                if p < e < q:
                    if q - e < RESTO and e - p >= RESTO:
                        removido.append((e, q, "resto de outro clipe"))
                        q = e
                    elif e - p < RESTO and q - e >= RESTO:
                        removido.append((p, e, "resto de outro clipe"))
                        p = e
            if q - p > 0.05:
                out.append([round(p, 3), round(q, 3)])
    return out, removido


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    r = detectar(sys.argv[1], refazer=True)
    for t in r["tapas"]:
        print(f"tapa em {hms(t['tapa'])} -> volta em {hms(t['retoma']) if t['retoma'] else 'fim'}")
    for x, y in r.get("bordas", []):
        print(f"sem rosto na ponta do take: {hms(x)}-{hms(y)}")
    print(f"{len(r['emendas'])} emendas entre clipes: " + ", ".join(hms(e) for e in r["emendas"]))
