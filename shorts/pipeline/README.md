# Pipeline de produção

    pip install kokoro-onnx soundfile pycairo
    python3 shorts/pipeline/episodes/<episodio>.py shorts/lote-AAAA-MM-DD/<arquivo>.mp4

- `core.py`: voz (Kokoro `am_michael`, offline, cache em `~/.cache`), linha do tempo, cabeçalho #N, legenda palavra por palavra, música sintetizada, −14 LUFS, H.264 1080×1920 30 fps. Baixa sozinho a fonte Poppins (OFL) e o modelo Kokoro na primeira execução.
- `illusions.py`: ilusões de ótica desenhadas por código (cada uma com parâmetro de revelação).
- `episodes/`: um roteiro por vídeo (`Seg` = falas + pausas + função de desenho).
