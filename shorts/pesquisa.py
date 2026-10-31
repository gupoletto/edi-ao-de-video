#!/usr/bin/env python3
"""Pesquisa de demanda no YouTube Shorts (EUA, inglês): mediana de views e destaques por busca.

    python3 shorts/pesquisa.py "how a jet engine works 3d" "what happens when a car crashes" --dias 30
    python3 shorts/pesquisa.py --arquivo buscas.txt --dias 7

Para cada busca: search.list (type=video, videoDuration=short, publishedAfter = N dias atrás, order=viewCount,
relevanceLanguage=en, regionCode=US, 25 resultados), depois videos.list com as estatísticas. Mostra a mediana de
views, os 3 vídeos mais vistos (canal e inscritos não; só título e views) e o "outlier de comentários" (maior
comentários/views entre os que passaram de 50 mil views; ESTRATEGIA.md, seção 2).
Cota: 100 unidades por busca + 1 por lote de estatísticas. 10 buscas = ~1.000 das 10.000 diárias.
"""
import datetime as dt
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upload  # noqa: E402


def buscar(token, q, dias, n=25):
    depois = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=dias)).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = upload.api_get(token, "search", part="id", q=q, type="video", videoDuration="short", publishedAfter=depois,
                       order="viewCount", relevanceLanguage="en", regionCode="US", maxResults=n)
    ids = [i["id"]["videoId"] for i in r.get("items", [])]
    if not ids:
        return []
    v = upload.api_get(token, "videos", part="statistics,snippet", id=",".join(ids))
    out = []
    for it in v["items"]:
        s = it["statistics"]
        out.append({"titulo": it["snippet"]["title"], "canal": it["snippet"]["channelTitle"],
                    "views": int(s.get("viewCount", 0)), "coments": int(s.get("commentCount", 0)),
                    "idioma": it["snippet"].get("defaultAudioLanguage", "") or it["snippet"].get("defaultLanguage", "")})
    return out


def main():
    args = sys.argv[1:]
    dias = 30
    if "--dias" in args:
        i = args.index("--dias")
        dias = int(args[i + 1])
        del args[i:i + 2]
    if "--arquivo" in args:
        i = args.index("--arquivo")
        args = args[:i] + [ln.strip() for ln in open(args[i + 1], encoding="utf-8") if ln.strip()] + args[i + 2:]
    token = upload.access_token()
    linhas = []
    for q in args:
        vs = [v for v in buscar(token, q, dias) if not v["idioma"] or v["idioma"].startswith("en")]
        if not vs:
            print(f"\n### {q}\nsem resultados")
            continue
        med = statistics.median(v["views"] for v in vs)
        linhas.append((med, q))
        print(f"\n### {q}  (mediana {med:,.0f} views, {len(vs)} vídeos, últimos {dias} dias)".replace(",", "."))
        for v in sorted(vs, key=lambda v: -v["views"])[:3]:
            print(f"- {v['views']:,} · {v['titulo'][:90]} ({v['canal']})".replace(",", "."))
        grandes = [v for v in vs if v["views"] >= 50000]
        if grandes:
            o = max(grandes, key=lambda v: v["coments"] / v["views"])
            print(f"- outlier de comentários: {100 * o['coments'] / o['views']:.2f} % · {o['titulo'][:80]}")
    print("\n## Ranking por mediana\n")
    for med, q in sorted(linhas, reverse=True):
        print(f"- {med:>12,.0f} · {q}".replace(",", "."))


if __name__ == "__main__":
    main()
