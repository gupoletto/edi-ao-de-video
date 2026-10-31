#!/usr/bin/env python3
"""Painel de desempenho dos Shorts do Fun Stuff, em Markdown (para colar em shorts/tendencias/AAAA-MM-DD.md).

    python3 shorts/metricas.py            # vídeos desde 27/10: tabela por vídeo + resumo por formato e por tópico
    python3 shorts/metricas.py --desde 2026-10-25                     # inclui o lote 1
    python3 shorts/metricas.py --desde 2026-11-02 --ate 2026-11-08   # só vídeos publicados nesse intervalo

Junta três fontes:
- uploaded.json de cada lote (id e data de publicação);
- historico.md (tópico e formato de cada arquivo);
- YouTube Data API (views, likes, comentários) e, se o token tiver o escopo yt-analytics.readonly, YouTube Analytics
  (duração média, % assistida, compartilhamentos, inscritos ganhos). O Analytics atrasa 2 a 3 dias.

Engajamento = (likes + comentários + compartilhamentos) / views. "Presa na amostra" = publicado há mais de 48 h e
com menos de 300 views (a amostra inicial de ~200 pessoas reprovou; ESTRATEGIA.md, seção 7).
"""
import datetime as dt
import glob
import json
import os
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upload  # noqa: E402

SHORTS = os.path.dirname(os.path.abspath(__file__))


def historico():
    """arquivo (lote/arquivo.mp4) -> (tópico, formato)."""
    out = {}
    for linha in open(os.path.join(SHORTS, "historico.md"), encoding="utf-8"):
        c = [x.strip() for x in linha.strip().strip("|").split("|")]
        if len(c) >= 6 and c[5].endswith(".mp4"):
            topico = c[1].split("(")[0].strip()
            out[c[5]] = (topico, c[3])
    return out


def videos():
    out = []
    for log in sorted(glob.glob(os.path.join(SHORTS, "lote-*", "uploaded.json"))):
        lote = os.path.basename(os.path.dirname(log))
        for arq, v in json.load(open(log, encoding="utf-8")).items():
            out.append({"id": v["id"], "arquivo": f"{lote}/{arq}", "publica": v["publishAt"]})
    return out


def formato_curto(f):
    f = f.lower()
    for chave, nome in (("quark", "Quark"), ("3d", "3D"), ("quiz", "Quiz"), ("interativo", "Quiz"),
                        ("ranking", "Ranking"), ("what if", "What if/why"), ("why", "What if/why")):
        if chave in f:
            return nome
    return f or "?"


def analytics(token, ids, inicio):
    """id -> {avd, pct, shares, subs}; vazio se o escopo não foi dado."""
    q = urllib.parse.urlencode({
        "ids": "channel==MINE", "startDate": inicio, "endDate": dt.date.today().isoformat(),
        "metrics": "views,averageViewDuration,averageViewPercentage,shares,subscribersGained",
        "dimensions": "video", "filters": "video==" + ",".join(ids), "maxResults": 200})
    req = urllib.request.Request("https://youtubeanalytics.googleapis.com/v2/reports?" + q,
                                 headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"> Analytics indisponível (HTTP {e.code}); só estatísticas públicas.\n")
        return {}
    # linha com 0 views no Analytics = dado ainda não processado (atraso de 2–3 dias): trata como ausente
    return {row[0]: {"avd": row[2], "pct": row[3], "shares": row[4], "subs": row[5]}
            for row in d.get("rows", []) if row[1] and row[2]}


def main():
    # padrão: desde 27/10, quando começou o formato atual (o lote 1, satisfying genérico, distorce as medianas)
    desde = sys.argv[sys.argv.index("--desde") + 1] if "--desde" in sys.argv else "2026-10-27"
    ate = sys.argv[sys.argv.index("--ate") + 1] if "--ate" in sys.argv else "2999-12-31"
    agora = dt.datetime.now(dt.timezone.utc)
    hist = historico()
    vs = [v for v in videos() if desde <= v["publica"][:10] <= ate and upload.parse(v["publica"]) <= agora]
    if not vs:
        sys.exit("nenhum vídeo publicado no intervalo")
    token = upload.access_token()
    stats = {}
    for i in range(0, len(vs), 50):
        r = upload.api_get(token, "videos", part="statistics,snippet", id=",".join(v["id"] for v in vs[i:i + 50]))
        for it in r["items"]:
            stats[it["id"]] = (it["statistics"], it["snippet"]["title"])
    an = analytics(token, [v["id"] for v in vs], min(v["publica"][:10] for v in vs))
    linhas = []
    for v in vs:
        s, titulo = stats.get(v["id"], ({}, "?"))
        views, likes, coments = (int(s.get(k, 0)) for k in ("viewCount", "likeCount", "commentCount"))
        a = an.get(v["id"], {})
        eng = (likes + coments + a.get("shares", 0)) / views if views else 0.0
        horas = (agora - upload.parse(v["publica"])).total_seconds() / 3600
        topico, formato = hist.get(v["arquivo"], ("?", "?"))
        linhas.append({**v, "titulo": titulo, "views": views, "likes": likes, "coments": coments, "eng": eng,
                       "avd": a.get("avd"), "pct": a.get("pct"), "subs": a.get("subs"), "horas": horas,
                       "topico": topico, "formato": formato_curto(formato),
                       "presa": horas > 48 and views < 300})
    print("| Publicado | Vídeo | Tópico | Formato | Views | Engaj. | Duração média | % assistida | Obs. |")
    print("|---|---|---|---|---:|---:|---:|---:|---|")
    for x in sorted(linhas, key=lambda x: x["publica"]):
        avd = f"{x['avd']} s" if x["avd"] is not None else "—"
        pct = f"{x['pct']:.0f} %" if x["pct"] is not None else "—"
        obs = "presa na amostra" if x["presa"] else ""
        print(f"| {x['publica'][:10]} | {x['titulo'][:48]} | {x['topico']} | {x['formato']} | {x['views']:,} | "
              f"{100 * x['eng']:.1f} % | {avd} | {pct} | {obs} |".replace(",", "."))
    for chave, nome in (("formato", "formato"), ("topico", "tópico")):
        print(f"\n**Por {nome}** (mediana de views; engajamento e % assistida médios)\n")
        print(f"| {nome.capitalize()} | Vídeos | Mediana de views | Engaj. | % assistida |")
        print("|---|---:|---:|---:|---:|")
        grupos = {}
        for x in linhas:
            if x["horas"] >= 24:  # vídeos com menos de 1 dia distorcem a mediana
                grupos.setdefault(x[chave], []).append(x)
        for g, xs in sorted(grupos.items(), key=lambda kv: -statistics.median(x["views"] for x in kv[1])):
            pcts = [x["pct"] for x in xs if x["pct"] is not None]
            pct = f"{statistics.mean(pcts):.0f} %" if pcts else "—"
            print(f"| {g} | {len(xs)} | {statistics.median(x['views'] for x in xs):,.0f} | "
                  f"{100 * statistics.mean(x['eng'] for x in xs):.1f} % | {pct} |".replace(",", "."))


if __name__ == "__main__":
    main()
