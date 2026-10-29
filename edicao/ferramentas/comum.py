"""Caminhos, instalação sob demanda e utilidades do editor de vídeos pessoais."""
import json
import os
import subprocess
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # edicao/
BRUTO, ESTILO, TRABALHO, FINAL = (os.path.join(RAIZ, d) for d in ("bruto", "estilo", "trabalho", "final"))
CACHE = os.path.expanduser("~/.cache")
FONTES = os.path.expanduser("~/.local/share/fonts")

SHERPA = os.path.join(CACHE, "sherpa")
SHERPA_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/"
FONT_URLS = {  # todas com licença OFL
    "Poppins-Bold.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-Bold.ttf",
    "Poppins-ExtraBold.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-ExtraBold.ttf",
    "Poppins-ExtraBoldItalic.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-ExtraBoldItalic.ttf",
    "Poppins-SemiBold.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-SemiBold.ttf",
    "SourceSerif4-Regular.ttf": "https://raw.githubusercontent.com/adobe-fonts/source-serif/release/TTF/SourceSerif4-Regular.ttf",
    "SourceSerif4-Semibold.ttf": "https://raw.githubusercontent.com/adobe-fonts/source-serif/release/TTF/SourceSerif4-Semibold.ttf",
}


def preparar(stt=False, turbo=False):
    """Baixa fontes (e, se pedido, o modelo de transcrição) na primeira vez."""
    os.makedirs(FONTES, exist_ok=True)
    novas = False
    for nome, url in FONT_URLS.items():
        p = os.path.join(FONTES, nome)
        if not os.path.exists(p):
            urllib.request.urlretrieve(url, p)
            novas = True
    if novas:
        subprocess.run(["fc-cache", "-f"], check=True)
    if stt:
        os.makedirs(SHERPA, exist_ok=True)
        modelo = "turbo" if turbo else "small"
        if not os.path.exists(os.path.join(SHERPA, f"sherpa-onnx-whisper-{modelo}")):
            tar = os.path.join(SHERPA, "w.tar.bz2")
            print(f"baixando o modelo de transcrição (Whisper {modelo})...", flush=True)
            urllib.request.urlretrieve(SHERPA_URL + f"sherpa-onnx-whisper-{modelo}.tar.bz2", tar)
            subprocess.run(["tar", "xjf", tar, "-C", SHERPA], check=True)
            os.remove(tar)
        vad = os.path.join(SHERPA, "silero_vad.onnx")
        if not os.path.exists(vad):
            urllib.request.urlretrieve(SHERPA_URL + "silero_vad.onnx", vad)


def pasta_trabalho(fonte):
    nome = os.path.splitext(os.path.basename(fonte))[0]
    p = os.path.join(TRABALHO, nome)
    os.makedirs(p, exist_ok=True)
    return p


def sonda(fonte):
    """Largura, altura, fps e duração do vídeo."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate:format=duration", "-of", "json", fonte],
                       capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    s = j["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return {"w": s["width"], "h": s["height"], "fps": float(num) / float(den), "dur": float(j["format"]["duration"])}


def ler(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def gravar(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def hms(t):
    m, s = divmod(max(0.0, t), 60)
    return f"{int(m):02d}:{s:04.1f}"


def erro(msg):
    sys.exit("erro: " + msg)
