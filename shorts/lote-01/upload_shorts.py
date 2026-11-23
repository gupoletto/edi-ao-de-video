#!/usr/bin/env python3
"""Upload the Fun Stuff Shorts to YouTube (Data API v3) with title, description, tags and a schedule.

Run on YOUR computer, in this folder:
    pip install google-api-python-client google-auth-oauthlib
    python upload_shorts.py --dry-run     # check everything, uploads nothing
    python upload_shorts.py               # upload

Needs client_secret.json (OAuth client of type "Desktop app") in this folder.
The first run opens your browser to sign in; the login is saved in token.json (keep it private).
Already-uploaded videos are recorded in uploaded.json and skipped on later runs.
"""
import json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def auth():
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    tok = os.path.join(HERE, "token.json")
    creds = Credentials.from_authorized_user_file(tok, SCOPES) if os.path.exists(tok) else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            secret = os.path.join(HERE, "client_secret.json")
            if not os.path.exists(secret):
                sys.exit("client_secret.json not found in this folder (see LEIA-ME.md, step 1).")
            creds = InstalledAppFlow.from_client_secrets_file(secret, SCOPES).run_local_server(port=0)
        with open(tok, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def ensure_file(v):
    path = os.path.join(HERE, v["file"])
    if os.path.exists(path):
        return path
    if v.get("url"):
        print(f"  downloading {v['file']} ...")
        try:
            urllib.request.urlretrieve(v["url"], path)
            return path
        except Exception as e:
            print(f"  could not download ({e}). The link may have expired — put {v['file']} in this folder manually.")
    return None


def main():
    dry = "--dry-run" in sys.argv
    with open(os.path.join(HERE, "videos.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    log_path = os.path.join(HERE, "uploaded.json")
    done = json.load(open(log_path, encoding="utf-8")) if os.path.exists(log_path) else {}
    yt = None
    for v in manifest["videos"]:
        print(f"\n== {v['title']}")
        if v["file"] in done:
            print(f"  already uploaded: {done[v['file']]['url']}")
            continue
        path = ensure_file(v)
        if not path:
            print(f"  SKIPPED: {v['file']} not found")
            continue
        body = {
            "snippet": {
                "title": v["title"][:100],
                "description": v["description"],
                "tags": v["tags"],
                "categoryId": v.get("categoryId", "28"),
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en",
            },
            "status": {
                "privacyStatus": "private",           # required for scheduling
                "publishAt": v["publishAt"],          # goes public automatically at this time (UTC)
                "selfDeclaredMadeForKids": False,
                "containsSyntheticMedia": False,
            },
        }
        size = os.path.getsize(path) / 1e6
        print(f"  file: {v['file']} ({size:.1f} MB) · goes public at {v['publishAt']} UTC")
        if dry:
            continue
        if yt is None:
            yt = auth()
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
        req = yt.videos().insert(part="snippet,status", body=body,
                                 media_body=MediaFileUpload(path, mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True))
        resp, tries = None, 0
        while resp is None:
            try:
                status, resp = req.next_chunk()
                if status:
                    print(f"  {int(status.progress() * 100)}%")
            except HttpError as e:
                if e.resp.status in (500, 502, 503, 504) and tries < 5:
                    tries += 1; time.sleep(2 ** tries); continue
                raise
        vid = resp["id"]
        done[v["file"]] = {"id": vid, "url": f"https://youtube.com/shorts/{vid}", "publishAt": v["publishAt"]}
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(done, f, indent=2)
        print(f"  OK -> https://youtube.com/shorts/{vid}")
    print("\nDone." + (" (dry run, nothing uploaded)" if dry else ""))


if __name__ == "__main__":
    main()
