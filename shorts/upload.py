#!/usr/bin/env python3
"""Upload a batch of Shorts to YouTube (Data API v3), scheduled into the channel's daily slots.

    python3 shorts/upload.py shorts/lote-02            # upload
    python3 shorts/upload.py shorts/lote-02 --dry-run  # check only, uploads nothing

Credentials come from the environment: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
No third-party packages needed.

Each batch folder holds videos.json (same format as lote-01) and the .mp4 files.
Uploads are recorded in <batch>/uploaded.json and skipped on later runs.
A video whose publishAt is missing, too close (< 2h), or already taken by another
upload is moved to the next free slot (SLOTS_UTC, one video per slot).
"""
import datetime as dt
import glob
import json
import os
import sys
import urllib.parse
import urllib.request

SHORTS = os.path.dirname(os.path.abspath(__file__))
SLOTS_UTC = [15, 19, 23]  # 12h, 16h, 20h Brasilia · 11h, 15h, 19h New York (EDT)
MIN_LEAD = dt.timedelta(hours=2)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def taken_slots():
    taken = set()
    for log in glob.glob(os.path.join(SHORTS, "*", "uploaded.json")):
        with open(log, encoding="utf-8") as f:
            taken.update(v["publishAt"] for v in json.load(f).values())
    return taken


def next_free_slot(after, taken):
    day = after.replace(hour=0, minute=0, second=0, microsecond=0)
    while True:
        for h in SLOTS_UTC:
            t = day.replace(hour=h)
            if t >= after and iso(t) not in taken:
                return t
        day += dt.timedelta(days=1)


def access_token():
    missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if missing:
        sys.exit("missing environment variables: " + ", ".join(missing))
    data = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data) as r:
        return json.load(r)["access_token"]


def upload(token, path, body):
    size = os.path.getsize(path)
    req = urllib.request.Request(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(size),
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        session_url = r.headers["Location"]
    with open(path, "rb") as f:
        put = urllib.request.Request(session_url, data=f.read(), method="PUT",
                                     headers={"Content-Type": "video/mp4", "Content-Length": str(size)})
    with urllib.request.urlopen(put, timeout=600) as r:
        return json.load(r)["id"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    batch, dry = os.path.abspath(args[0]), "--dry-run" in sys.argv
    with open(os.path.join(batch, "videos.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    log_path = os.path.join(batch, "uploaded.json")
    done = json.load(open(log_path, encoding="utf-8")) if os.path.exists(log_path) else {}
    taken = taken_slots()
    earliest = dt.datetime.now(dt.timezone.utc) + MIN_LEAD
    token = None
    for v in manifest["videos"]:
        print(f"\n== {v['title']}")
        if v["file"] in done:
            print(f"  already uploaded: {done[v['file']]['url']}")
            continue
        path = os.path.join(batch, v["file"])
        if not os.path.exists(path):
            print(f"  SKIPPED: {v['file']} not found")
            continue
        when = v.get("publishAt")
        if not when or parse(when) < earliest or when in taken:
            when = iso(next_free_slot(earliest, taken))
            print(f"  rescheduled to {when}")
        taken.add(when)
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
                "privacyStatus": "private",  # required for scheduling
                "publishAt": when,
                "selfDeclaredMadeForKids": False,
                "containsSyntheticMedia": bool(v.get("containsSyntheticMedia", False)),
            },
        }
        print(f"  file: {v['file']} ({os.path.getsize(path) / 1e6:.1f} MB) · goes public at {when} UTC")
        if dry:
            continue
        token = token or access_token()
        vid = upload(token, path, body)
        done[v["file"]] = {"id": vid, "url": f"https://youtube.com/shorts/{vid}", "publishAt": when}
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(done, f, indent=2)
        print(f"  OK -> https://youtube.com/shorts/{vid}")
    print("\nDone." + (" (dry run, nothing uploaded)" if dry else ""))


if __name__ == "__main__":
    main()
