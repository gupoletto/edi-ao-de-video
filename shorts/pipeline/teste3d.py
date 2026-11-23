"""Quadros de teste de um episódio 3D (enquadramento, antes do render completo de ~15-20 min):

    python3 shorts/pipeline/teste3d.py tres_turbina 0.5 6 12 20   # -> $TESTE3D_SAIDA/t3d.png (padrão /tmp)

Renderiza só os instantes pedidos (segundos do vídeo), com cabeçalho, legenda e a zona segura dos Shorts por cima
(vermelho = a interface do app cobre), e monta uma folha de contato."""
import sys, os, importlib, cairo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from PIL import Image
ep = importlib.import_module("episodes." + sys.argv[1])
ts = [float(x) for x in sys.argv[2:]]
segs = [s.build() for s in ep.SEGMENTS]
t0 = 0
for s in segs:
    s.t0 = t0; t0 += s.dur
print("total", round(t0, 1), [round(s.dur, 1) for s in segs])
ep.FILME.renderizar(segs, t0, tempos=ts)
S = os.environ.get('TESTE3D_SAIDA', '/tmp')
zp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'anuncios', 'zonas', 'shorts.png')
if not os.path.exists(zp):
    import subprocess
    subprocess.run([sys.executable, os.path.join(os.path.dirname(zp), '..', 'zonas.py')], check=True)
z = Image.open(zp).convert('RGBA')
folha = Image.new('RGB', (270 * len(ts), 480))
for j, t in enumerate(ts):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    s = segs[k]
    jpg = os.path.join(ep.FILME.pasta, f"{j:05d}.jpg")
    im = Image.open(jpg).convert('RGB')
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, core.W, core.H); c = cairo.Context(surf)
    im.save(f'{S}/q.png'); fundo = cairo.ImageSurface.create_from_png(f'{S}/q.png')
    c.set_source_surface(fundo); c.paint()
    core.draw_header(c, s.header); core.draw_captions(c, s, t - s.t0)
    surf.write_to_png(f'{S}/q.png')
    im = Image.alpha_composite(Image.open(f'{S}/q.png').convert('RGBA'), z).convert('RGB')
    folha.paste(im.resize((270, 480)), (j * 270, 0))
folha.save(f'{S}/t3d.png')
