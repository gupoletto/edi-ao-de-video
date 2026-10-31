#!/usr/bin/env python3
"""Upload a batch of Shorts to YouTube (Data API v3), scheduled into the channel's daily slots.

    python3 shorts/upload.py shorts/lote-02            # upload
    python3 shorts/upload.py shorts/lote-02 --dry-run  # check only, uploads nothing

Credentials come from the environment: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
No third-party packages needed.

Each batch folder holds videos.json (same format as lote-01) and the .mp4 files.
Uploads are recorded in <batch>/uploaded.json and skipped on later runs.
A video whose publishAt is missing, too close (< 30 min), or already taken by another
upload is moved to the next free peak slot (one video per slot). Slots follow US peak
viewing hours in New York time, so they track daylight saving automatically.
--limit=N uploads at most N videos in this run.

    python3 shorts/upload.py --free-slots 2026-10-27   # that day's peak slots still free (UTC)
"""
import datetime as dt
import glob
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

SHORTS = os.path.dirname(os.path.abspath(__file__))
AUDIENCE_TZ = ZoneInfo("America/New_York")
# Go live shortly before each US Shorts peak: lunch, after school/work, evening.
SLOTS_WEEKDAY = [12, 15, 19]
SLOTS_WEEKEND = [10, 14, 19]
# Test (approved by the owner on 31/10/2026): 2 Shorts a day for one week, so each one gets more room before the
# next. Lunch and evening peaks; back to 3 a day after the end date unless PLANO.md says otherwise.
TESTE_2_POR_DIA = (dt.date(2026, 11, 2), dt.date(2026, 11, 8))
SLOTS_TESTE_WEEKDAY = [12, 19]
SLOTS_TESTE_WEEKEND = [10, 19]
MIN_LEAD = dt.timedelta(minutes=30)


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


def day_slots(day):
    fim_de_semana = day.weekday() >= 5
    if TESTE_2_POR_DIA[0] <= day <= TESTE_2_POR_DIA[1]:
        hours = SLOTS_TESTE_WEEKEND if fim_de_semana else SLOTS_TESTE_WEEKDAY
    else:
        hours = SLOTS_WEEKEND if fim_de_semana else SLOTS_WEEKDAY
    return [dt.datetime(day.year, day.month, day.day, h, tzinfo=AUDIENCE_TZ).astimezone(dt.timezone.utc) for h in hours]


def next_free_slot(after, taken):
    day = after.astimezone(AUDIENCE_TZ).date()
    while True:
        for t in day_slots(day):
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


def api_get(token, path, **params):
    url = "https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})) as r:
        return json.load(r)


def channel_videos(token):
    """Title -> {id, publishAt} for every video already on the channel, scheduled ones included.

    The channel itself is the source of truth, so a run that could not push uploaded.json
    never causes a duplicate upload.
    """
    channel = api_get(token, "channels", part="contentDetails", mine="true")["items"][0]
    uploads = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], None
    while True:
        params = {"part": "contentDetails", "playlistId": uploads, "maxResults": 50}
        if page:
            params["pageToken"] = page
        res = api_get(token, "playlistItems", **params)
        ids += [i["contentDetails"]["videoId"] for i in res["items"]]
        page = res.get("nextPageToken")
        if not page:
            break
    found = {}
    for i in range(0, len(ids), 50):
        for v in api_get(token, "videos", part="snippet,status", id=",".join(ids[i:i + 50]))["items"]:
            found[v["snippet"]["title"]] = {"id": v["id"], "publishAt": v["status"].get("publishAt")}
    return found


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


def pending_slots():
    """publishAt of videos already planned in some batch but not uploaded yet."""
    pending = set()
    for manifest in glob.glob(os.path.join(SHORTS, "*", "videos.json")):
        log = os.path.join(os.path.dirname(manifest), "uploaded.json")
        done = json.load(open(log, encoding="utf-8")) if os.path.exists(log) else {}
        with open(manifest, encoding="utf-8") as f:
            pending.update(v["publishAt"] for v in json.load(f)["videos"] if v.get("publishAt") and v["file"] not in done)
    return pending


def free_slots(day_str):
    taken = taken_slots() | pending_slots()
    if all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")):
        try:
            taken.update(v["publishAt"] for v in channel_videos(access_token()).values() if v["publishAt"])
        except urllib.error.HTTPError as e:
            print(f"warning: could not read the channel ({e}); using uploaded.json only", file=sys.stderr)
    earliest = dt.datetime.now(dt.timezone.utc) + MIN_LEAD
    for t in day_slots(dt.date.fromisoformat(day_str)):
        if t >= earliest and iso(t) not in taken:
            print(iso(t))


def main():
    if "--free-slots" in sys.argv:
        return free_slots(sys.argv[sys.argv.index("--free-slots") + 1])
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    batch, dry = os.path.abspath(args[0]), "--dry-run" in sys.argv
    limit = next((int(a.split("=", 1)[1]) for a in sys.argv if a.startswith("--limit=")), None)
    with open(os.path.join(batch, "videos.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    log_path = os.path.join(batch, "uploaded.json")
    done = json.load(open(log_path, encoding="utf-8")) if os.path.exists(log_path) else {}
    taken = taken_slots()
    earliest = dt.datetime.now(dt.timezone.utc) + MIN_LEAD
    token, sent, on_channel = None, 0, {}
    if not dry:
        token = access_token()
        on_channel = channel_videos(token)
        taken.update(v["publishAt"] for v in on_channel.values() if v["publishAt"])
    for v in manifest["videos"]:
        print(f"\n== {v['title']}")
        if v["file"] in done:
            print(f"  already uploaded: {done[v['file']]['url']}")
            continue
        existing = on_channel.get(v["title"][:100])
        if existing:
            vid = existing["id"]
            done[v["file"]] = {"id": vid, "url": f"https://youtube.com/shorts/{vid}",
                               "publishAt": existing["publishAt"] or ""}
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(done, f, indent=2)
            print(f"  already on the channel: https://youtube.com/shorts/{vid} (recorded)")
            continue
        if limit is not None and sent >= limit:
            print("  left for a later run (--limit)")
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
        sent += 1
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
        vid = upload(token, path, body)
        done[v["file"]] = {"id": vid, "url": f"https://youtube.com/shorts/{vid}", "publishAt": when}
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(done, f, indent=2)
        print(f"  OK -> https://youtube.com/shorts/{vid}")
    print("\nDone." + (" (dry run, nothing uploaded)" if dry else ""))


if __name__ == "__main__":
    main()
