"""Publish a local image or video to Instagram (feed post, story or reel).

Usage:
  python3 post_to_instagram.py <file> <caption.txt> <feed|story|reel>
  python3 post_to_instagram.py --check
  python3 post_to_instagram.py --refresh

Env: IG_TOKEN, IG_USER_ID.
The file is uploaded to Litterbox (litterbox.catbox.moe, auto-deletes after 12h) so
Instagram can fetch it; needs network access to litterbox.catbox.moe, litter.catbox.moe
and graph.instagram.com.
"""
import json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://graph.instagram.com/v23.0"
token = os.environ["IG_TOKEN"]


def call(method, path, base=API, **params):
    params["access_token"] = token
    data = urllib.parse.urlencode(params).encode()
    req = (urllib.request.Request(f"{base}/{path}?{data.decode()}") if method == "GET"
           else urllib.request.Request(f"{base}/{path}", data=data, method="POST"))
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Instagram API error on {path}: {e.read().decode()[:500].replace(token, '[TOKEN]')}")


def upload(path):
    for attempt in range(3):
        r = subprocess.run(["curl", "-sS", "--max-time", "120", "-F", "reqtype=fileupload", "-F", "time=12h",
                            "-F", f"fileToUpload=@{path}",
                            "https://litterbox.catbox.moe/resources/internals/api.php"],
                           capture_output=True, text=True)
        url = r.stdout.strip()
        if url.startswith("https://"):
            return url
        time.sleep(5)
    sys.exit(f"Image host upload failed: {r.stdout[:200]} {r.stderr[:200]}")


if sys.argv[1] == "--check":
    print(json.dumps(call("GET", "me", fields="user_id,username,account_type")))
    sys.exit(0)
if sys.argv[1] == "--refresh":
    r = call("GET", "refresh_access_token", base="https://graph.instagram.com", grant_type="ig_refresh_token")
    print(json.dumps({"access_token": r["access_token"], "expires_in_days": r.get("expires_in", 0) // 86400}))
    sys.exit(0)

path, cap_file, mode = sys.argv[1], sys.argv[2], sys.argv[3]
ig_user = os.environ["IG_USER_ID"]
caption = open(cap_file).read().strip()
url = upload(path)
time.sleep(3)

if mode == "story":
    key = "video_url" if path.lower().endswith(".mp4") else "image_url"
    c = call("POST", f"{ig_user}/media", media_type="STORIES", **{key: url})
elif mode == "reel":
    c = call("POST", f"{ig_user}/media", media_type="REELS", video_url=url, caption=caption, share_to_feed="true")
else:
    c = call("POST", f"{ig_user}/media", image_url=url, caption=caption)
cid = c["id"]

for _ in range(60):
    s = call("GET", cid, fields="status_code").get("status_code")
    if s == "FINISHED":
        break
    if s in ("ERROR", "EXPIRED"):
        sys.exit(f"Container {cid} failed: {s}")
    time.sleep(5)

pid = call("POST", f"{ig_user}/media_publish", creation_id=cid)["id"]
link = call("GET", pid, fields="permalink").get("permalink", "")
print(json.dumps({"posted": mode, "media_id": pid, "permalink": link}))
