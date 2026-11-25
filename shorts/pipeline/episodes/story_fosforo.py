"""How are matches made? (2D, padrão caprichado). Wed 25/11/2026. Search 25/11: "how matches are made" median 1.86M.

Facts:
- the first lighter came before the friction match: Johann Döbereiner's hydrogen lamp (1823); John Walker sold the
  first friction matches in 1826/1827;
- logs (aspen or pine) are peeled into thin sheets of veneer and chopped into splints (match sticks);
- splints are soaked in a fire retardant (ammonium phosphate) so the stick doesn't keep glowing after it's blown out,
  then dipped in paraffin wax so the flame can climb from the head to the wood;
- the head: potassium chlorate (oxygen source), sulfur and glue, plus powdered glass for friction;
- early matches used white phosphorus, which poisoned factory workers ("phossy jaw") and was banned in the early
  1900s; safety matches (Sweden, 1850s) moved red phosphorus to the striker on the box, so the match only lights
  there.
Tone: curious/history -> cinema? Use "curioso" -> lofi. Prefer misterio for the fire glow? -> cinema.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "historia"   # -> cinema
MADEIRA = (0.92, 0.80, 0.58)
CABECA = (0.80, 0.12, 0.10)
CHAMA = (1.0, 0.65, 0.18)
AMAR = (1.0, 0.85, 0.35)
FUNDO = ((0.14, 0.10, 0.09), (0.03, 0.02, 0.02))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def chama(ctx, x, y, s, t):
    anim.brilho(ctx, x, y - 20 * s, 140 * s, CHAMA, 0.7)
    for k, (cor, esc) in enumerate(((CHAMA, 1.0), (AMAR, 0.65), ((1, 1, 0.9), 0.3))):
        h = 90 * s * esc * (1 + 0.08 * math.sin(t * 13 + k))
        w = 34 * s * esc
        ctx.new_path()
        ctx.move_to(x, y - h)
        ctx.curve_to(x + w, y - h * 0.5, x + w, y, x, y + 8 * s)
        ctx.curve_to(x - w, y, x - w, y - h * 0.5, x, y - h)
        ctx.set_source_rgb(*cor)
        ctx.fill()


def fosforo(ctx, x, y, ang=0.0, s=1.0, cabeca=True, cor_cab=CABECA, aceso=False, t=0.0):
    """Palito com cabeça; (x, y) = base do palito."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ctx.new_path()
    ctx.rectangle(-9, -260, 18, 260)
    ctx.set_source_rgb(*MADEIRA)
    ctx.fill()
    ctx.rectangle(-9, -260, 6, 260)
    ctx.set_source_rgba(0, 0, 0, 0.12)
    ctx.fill()
    if cabeca:
        anim.esfera(ctx, 0, -272, 22, cor_cab)
    if aceso:
        chama(ctx, 0, -280, 1.0, t)
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=CHAMA)
    # um isqueiro antigo (lampião de vidro) à esquerda, o fósforo à direita: datas correndo
    anim.sombra_chao(ctx, 330, 1120, 260)
    anim.cilindro(ctx, 330, 820, 170, 300, (0.78, 0.86, 0.92))
    anim.cilindro(ctx, 330, 760, 60, 60, (0.55, 0.45, 0.30))
    chama(ctx, 330, 745, 0.8, t)
    fosforo(ctx, 760, 1120, 0.1, 1.0, t=t)
    anim.contador(ctx, t - 0.2, 330, 600, 1823, ini=1800, dur=1.0, fmt="{:.0f}", size=80, cor=AMAR, som=None)
    if len(s.items) > 1:
        m = s.mark(1)
        anim.contador(ctx, t - m, 760, 600, 1826, ini=1800, dur=0.8, fmt="{:.0f}", size=80, cor=WHITE, som=None)
        anim.texto_pop(ctx, t - m - 0.3, ["LIGHTER", "FIRST"], 540, 470 + 50, size=72, cor=CHAMA, largura=900)


def d_toras(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.22, 0.17, 0.12), (0.05, 0.04, 0.03), bokeh=(1, 0.9, 0.7))
    giro = t * 3   # tora girando e soltando uma lâmina fina
    anim.sombra_chao(ctx, 400, 1150, 360)
    ctx.save()
    ctx.translate(400, 900)
    ctx.new_path()
    ctx.arc(0, 0, 150, 0, 2 * math.pi)
    ctx.set_source_rgb(0.62, 0.45, 0.28)
    ctx.fill()
    ctx.set_source_rgba(0.42, 0.30, 0.18, 1)
    ctx.set_line_width(3)
    for r in range(20, 150, 22):
        ctx.arc(0, 0, r, giro, giro + 5.5)
        ctx.stroke()
    ctx.restore()
    ctx.set_source_rgb(*MADEIRA)   # lâmina saindo
    ctx.move_to(400, 750)
    ctx.curve_to(600, 740, 700, 760, 900, 760)
    ctx.line_to(900, 772)
    ctx.curve_to(700, 772, 600, 752, 400, 762)
    ctx.close_path()
    ctx.fill()
    for i in range(10):   # palitos picados caindo
        f = (t * 1.2 + i * 0.1) % 1.0
        fosforo(ctx, 760 + (i % 4) * 40, 800 + f * 380, 0.6 * math.sin(i + t * 4), 0.35, cabeca=False)
    anim.contador(ctx, t - 1.0, 540, 560, 1000000, dur=1.5, sufixo=" STICKS", size=72, cor=AMAR)


def d_banho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(0.7, 0.9, 1.0))
    sobe = ease((t - 0.4) / 0.7) - ease((t - 1.8) / 0.6)
    anim.sombra_chao(ctx, 540, 1180, 700)
    anim.bloco_3d(ctx, 190, 1010, 700, 160, 50, (0.40, 0.65, 0.85))   # tanque de retardante
    for i in range(9):
        fosforo(ctx, 250 + i * 70, 1000 - 220 * sobe, 0.0, 0.8, cabeca=False)
    if len(s.items) > 1:
        m = s.mark(1)
        anim.texto_pop(ctx, t - m, ["THEN", "WAX"], 540, 560, size=84, cor=AMAR)
        anim.anel_destaque(ctx, t - m - 0.3, 540, 800, 120, cor=AMAR)
    else:
        anim.texto_pop(ctx, t - 0.5, ["NO", "GLOWING"], 540, 560, size=84, cor=(0.6, 0.85, 1.0))


def d_cabeca(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=CHAMA)
    itens = [("OXYGEN SALT", (0.95, 0.95, 0.95), 260), ("SULFUR", (0.98, 0.88, 0.25), 540),
             ("GROUND GLASS", (0.75, 0.90, 0.95), 820)]
    for i, (nome, cor, x) in enumerate(itens):
        ti = t - 0.3 - i * 0.7
        core.evento_som("pop", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.45), 0.001)
        ctx.save()
        ctx.translate(x, 880)
        ctx.scale(k, k)
        anim.sombra_chao(ctx, 0, 90, 200)
        for j in range(6):
            anim.esfera(ctx, (j % 3) * 46 - 46, 40 - (j // 3) * 42, 30, cor)
        ctx.restore()
        text_center(ctx, nome, x, 1010, 30, WHITE, "ExtraBold", alpha=min(1.0, ti * 3))
    if len(s.items) > 1:
        m = s.mark(1)
        mergulha = ease((t - m) / 0.5)
        fosforo(ctx, 540, 1180 + 120 * (1 - mergulha), 0.0, 1.0, t=t)
        anim.anel_destaque(ctx, t - m - 0.4, 540, 1180 - 272, 60, cor=AMAR, som=None)


def d_fosforo_branco(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.14, 0.18, 0.12), (0.03, 0.04, 0.03), bokeh=(0.7, 1, 0.6))
    fosforo(ctx, 540, 1150, 0.0, 1.2, cor_cab=(0.96, 0.96, 0.88), t=t)
    anim.brilho(ctx, 540, 1150 - 326, 160, (0.6, 1.0, 0.5), 0.6 + 0.2 * math.sin(t * 4))   # brilho verde, tóxico
    anim.texto_pop(ctx, t - 0.4, ["TOXIC", "WHITE", "PHOSPHORUS"], 540, 540, size=74, cor=(0.7, 1, 0.6),
                   cor_destaque=WHITE, destaque=1)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["BANNED"], 540, 740, size=96, cor=(1, 0.35, 0.3))
        anim.estouro(ctx, t - s.mark(1), 540, 720, cor=(1, 0.35, 0.3), r0=180, r1=320)


def d_caixa(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=CHAMA)
    anim.sombra_chao(ctx, 540, 1040, 640)
    anim.bloco_3d(ctx, 250, 820, 560, 200, 60, (0.85, 0.20, 0.15))   # caixa de fósforos (acima da legenda)
    ctx.set_source_rgb(0.35, 0.18, 0.12)   # lixa com fósforo vermelho
    ctx.rectangle(250, 960, 560, 40)
    ctx.fill()
    risca = ease((t - 0.8) / 0.4)
    x = 300 + 460 * risca
    aceso = t > 1.25
    fosforo(ctx, x, 1150, -1.0 + 0.3 * risca, 1.0, aceso=aceso, t=t)
    anim.faiscas(ctx, t, x - 200, 970, n=20, vel=300, cor=AMAR) if 0.8 < t < 1.6 else None
    anim.estouro(ctx, t - 1.25, x - 210, 900, cor=CHAMA, r0=60, r1=180)
    anim.seta(ctx, t - 0.2, 530, 965, ang=math.pi / 2, cor=WHITE)
    anim.texto_pop(ctx, t - 0.3, ["RED", "PHOSPHORUS", "ON", "THE", "BOX"], 540, 540, size=70, cor=WHITE,
                   cor_destaque=(1, 0.4, 0.35), destaque=1, intervalo=0.15)


SEGMENTS = [
    Seg(["Here's a weird one: the lighter was invented before the match.", "Three years before."], d_gancho,
        {"title": "HOW ARE MATCHES MADE?"}, tail=0.2),
    Seg(["Today, logs are peeled into thin sheets, and chopped into millions of tiny sticks."], d_toras,
        {"big": "STICKS", "color": MADEIRA}, tail=0.2),
    Seg(["The sticks get a chemical bath, so they don't keep glowing after you blow them out.",
         "Then a dip in wax, so the flame can climb onto the wood."], d_banho,
        {"big": "BATHS", "color": (0.6, 0.85, 1.0)}, tail=0.2),
    Seg(["The head is a mix of an oxygen rich salt, sulfur, and ground glass for friction.",
         "Each stick is dipped, and dried."], d_cabeca, {"big": "THE HEAD", "color": CABECA}, tail=0.2),
    Seg(["The first matches used white phosphorus. It poisoned the factory workers.", "So it was banned."],
        d_fosforo_branco, {"big": "THE DARK PART", "big_size": 92, "color": (0.7, 1, 0.6)}, tail=0.2),
    Seg(["Today's safety matches hide the phosphorus on the box. That's why they only light when you strike there."],
        d_caixa, {"big": "THE TRICK", "color": CHAMA}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Matches or lighter: which do you use?", "MATCHES OR LIGHTER?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO, bokeh=CHAMA)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
