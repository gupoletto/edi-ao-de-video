#!/usr/bin/env python3
"""Painel de desempenho dos Shorts do Fun Stuff, em Markdown (para colar em shorts/tendencias/AAAA-MM-DD.md).

    python3 shorts/metricas.py            # vídeos desde 27/10: tabela por vídeo + resumo por formato e por tópico
    python3 shorts/metricas.py --desde 2026-10-25                     # inclui o lote 1
    python3 shorts/metricas.py --desde 2026-11-02 --ate 2026-11-08   # só vídeos publicados nesse intervalo
    python3 shorts/metricas.py --retencao                              # + onde cada vídeo "vaza" (curva de retenção)

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


def duracao_s(iso):
    """PT1M2S -> 62."""
    import re
    m = re.match(r"PT(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0) if m else 0


def retencao(token, vid, inicio):
    """Curva de retenção [(fração do vídeo, % ainda assistindo)] do Analytics; [] se não houver dado ainda."""
    q = urllib.parse.urlencode({"ids": "channel==MINE", "startDate": inicio, "endDate": dt.date.today().isoformat(),
                                "metrics": "audienceWatchRatio", "dimensions": "elapsedVideoTimeRatio",
                                "filters": f"video=={vid}"})
    req = urllib.request.Request("https://youtubeanalytics.googleapis.com/v2/reports?" + q,
                                 headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as r:
            return [(row[0], row[1]) for row in json.load(r).get("rows", [])]
    except urllib.error.HTTPError:
        return []


def vazamentos(curva, dur):
    """Resumo da curva: quanto fica no 1º segundo, aos 25/50/75 % e no fim, e o trecho com a maior queda."""
    if len(curva) < 10 or not dur:
        return None
    def em(f):
        return min(curva, key=lambda c: abs(c[0] - f))[1]
    quedas = []
    passo = max(1, len(curva) // 20)  # janelas de ~5 % do vídeo
    for i in range(0, len(curva) - passo, passo):
        quedas.append((curva[i][1] - curva[i + passo][1], curva[i][0], curva[i + passo][0]))
    meio = [q for q in quedas if q[1] >= 0.05]  # ignora o 1º instante (o gancho é avaliado à parte)
    pior = max(meio) if meio else max(quedas)
    return {"1s": em(1 / dur), "25": em(0.25), "50": em(0.5), "75": em(0.75), "fim": curva[-1][1],
            "pior": (pior[0], pior[1] * dur, pior[2] * dur)}


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
    if "--retencao" in sys.argv:
        ids = [x["id"] for x in linhas if x["horas"] >= 48]
        durs = {}
        for i in range(0, len(ids), 50):
            for it in upload.api_get(token, "videos", part="contentDetails", id=",".join(ids[i:i + 50]))["items"]:
                durs[it["id"]] = duracao_s(it["contentDetails"]["duration"])
        print("\n**Retenção** (fração da audiência ainda assistindo; > 100 % no início = replays; \"vazamento\" = "
              "trecho de ~5 % do vídeo com a maior queda depois do gancho)\n")
        print("| Vídeo | Duração | 1º s | 25 % | 50 % | 75 % | Fim | Maior vazamento |")
        print("|---|---:|---:|---:|---:|---:|---:|---|")
        for x in sorted(linhas, key=lambda x: x["publica"]):
            if x["id"] not in durs:
                continue
            r = vazamentos(retencao(token, x["id"], x["publica"][:10]), durs[x["id"]])
            if not r:
                print(f"| {x['titulo'][:40]} | {durs[x['id']]} s | — | — | — | — | — | (sem dados ainda) |")
                continue
            q, a, b = r["pior"]
            print(f"| {x['titulo'][:40]} | {durs[x['id']]} s | {100 * r['1s']:.0f} % | {100 * r['25']:.0f} % | "
                  f"{100 * r['50']:.0f} % | {100 * r['75']:.0f} % | {100 * r['fim']:.0f} % | "
                  f"−{100 * q:.0f} pts entre {a:.0f} e {b:.0f} s |")
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
