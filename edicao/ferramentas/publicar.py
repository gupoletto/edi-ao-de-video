#!/usr/bin/env python3
"""Sobe um vídeo editado para o canal PESSOAL do usuário no YouTube, como privado, com a thumbnail.

    python3 edicao/ferramentas/publicar.py edicao/final/video3_editado_4k.mp4 --titulo "..." \\
        [--descricao arquivo.txt] [--thumb edicao/final/video3_thumb.jpg] [--publico nao_listado]

Credenciais (variáveis de ambiente da sessão, nunca no Git nem no chat):
  YT_CLIENT_ID, YT_CLIENT_SECRET     o mesmo app OAuth do Fun Stuff
  YT_PESSOAL_REFRESH_TOKEN           token autorizado na conta/canal pessoal (escopos youtube.upload + youtube.readonly)
  YT_PESSOAL_CANAL                   ID do canal pessoal (UC...): trava; só sobe se o token apontar para ele
Nunca sobe no canal do Fun Stuff (UCUVaO7rhj5SbRhkEJ09xptQ), nem se as variáveis estiverem trocadas.
O vídeo sobe como "private" (padrão) ou "unlisted": o usuário revisa e publica no YouTube Studio.
Upload retomável em blocos de 64 MB (arquivos 4K de vários GB).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

FUN_STUFF = "UCUVaO7rhj5SbRhkEJ09xptQ"
BLOCO = 64 * 1024 * 1024


def token():
    dados = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_PESSOAL_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", dados) as r:
        return json.load(r)["access_token"]


def canal(tk):
    req = urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true",
                                 headers={"Authorization": "Bearer " + tk})
    with urllib.request.urlopen(req) as r:
        itens = json.load(r).get("items", [])
    return (itens[0]["id"], itens[0]["snippet"]["title"]) if itens else (None, None)


def enviar(tk, arquivo, corpo):
    tam = os.path.getsize(arquivo)
    ini = urllib.request.Request(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        data=json.dumps(corpo).encode(), method="POST",
        headers={"Authorization": "Bearer " + tk, "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(tam)})
    with urllib.request.urlopen(ini) as r:
        url = r.headers["Location"]
    with open(arquivo, "rb") as f:
        pos = 0
        while pos < tam:
            pedaco = f.read(BLOCO)
            fim = pos + len(pedaco) - 1
            req = urllib.request.Request(url, data=pedaco, method="PUT", headers={
                "Authorization": "Bearer " + tk, "Content-Length": str(len(pedaco)),
                "Content-Range": f"bytes {pos}-{fim}/{tam}"})
            try:
                with urllib.request.urlopen(req) as r:
                    return json.load(r)  # último bloco: o YouTube devolve o vídeo
            except urllib.error.HTTPError as e:
                if e.code != 308:  # 308 = "continue mandando"
                    raise
            pos = fim + 1
            print(f"  {pos / tam:.0%}", flush=True)


def thumbnail(tk, video_id, jpg):
    with open(jpg, "rb") as f:
        req = urllib.request.Request(
            f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}", data=f.read(),
            method="POST", headers={"Authorization": "Bearer " + tk, "Content-Type": "image/jpeg"})
    with urllib.request.urlopen(req) as r:
        json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--descricao", help="arquivo .txt com a descrição")
    ap.add_argument("--tags", nargs="*", default=[])
    ap.add_argument("--thumb")
    ap.add_argument("--publico", default="private", choices=["private", "unlisted"])
    a = ap.parse_args()
    for v in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_PESSOAL_REFRESH_TOKEN", "YT_PESSOAL_CANAL"):
        if not os.environ.get(v):
            sys.exit(f"falta a variável de ambiente {v} (veja o topo deste arquivo)")
    tk = token()
    cid, nome = canal(tk)
    if cid == FUN_STUFF or cid != os.environ["YT_PESSOAL_CANAL"]:
        sys.exit(f"trava: o token aponta para {cid} ({nome}), não para o canal pessoal configurado. Nada foi enviado.")
    print(f"canal: {nome} ({cid})")
    descricao = open(a.descricao, encoding="utf-8").read() if a.descricao else ""
    corpo = {"snippet": {"title": a.titulo[:100], "description": descricao, "tags": a.tags, "categoryId": "22"},
             "status": {"privacyStatus": a.publico, "selfDeclaredMadeForKids": False}}
    v = enviar(tk, a.arquivo, corpo)
    print(f"enviado: https://youtu.be/{v['id']} ({a.publico})")
    if a.thumb:
        thumbnail(tk, v["id"], a.thumb)
        print("thumbnail aplicada")


if __name__ == "__main__":
    main()
