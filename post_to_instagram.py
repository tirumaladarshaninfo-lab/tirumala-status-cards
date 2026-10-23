"""Publish a local PNG to Instagram (feed post or story) via the Instagram API with Instagram Login.

Usage:
  python3 post_to_instagram.py <image.png> <caption.txt> <feed|story>
  python3 post_to_instagram.py --check       # verify token, print account + token expiry info
  python3 post_to_instagram.py --refresh     # refresh the 60-day token, print the new one

Env vars:
  IG_TOKEN     Instagram user access token (IGAA...), needs instagram_business_content_publish
  IG_USER_ID   Instagram account ID (17841...)
  GH_REPO      owner/repo of the PUBLIC GitHub repo that hosts images
  GH_CLONE     local clone path (default /home/claude/tirumala-status-cards)
Needs network access to graph.instagram.com. Images are pushed with git, then
fetched by Instagram from raw.githubusercontent.com.
"""
import datetime, json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://graph.instagram.com/v23.0"
token = os.environ["IG_TOKEN"]


def call(method, path, base=API, **params):
    params["access_token"] = token
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(f"{base}/{path}?{data.decode()}")
    else:
        req = urllib.request.Request(f"{base}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500].replace(token, "[TOKEN]")
        sys.exit(f"Instagram API error on {path}: {body}")


if sys.argv[1] == "--check":
    print(json.dumps(call("GET", "me", fields="user_id,username,account_type")))
    sys.exit(0)
if sys.argv[1] == "--refresh":
    r = call("GET", "refresh_access_token", base="https://graph.instagram.com", grant_type="ig_refresh_token")
    print(json.dumps({"access_token": r["access_token"], "expires_in_days": r.get("expires_in", 0) // 86400}))
    sys.exit(0)

img, cap_file, mode = sys.argv[1], sys.argv[2], sys.argv[3]
ig_user, repo = os.environ["IG_USER_ID"], os.environ["GH_REPO"]

# 1. Host the image publicly on GitHub (unique name so caches never serve an old card)
stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
dest = f"posts/{stamp}-{mode}.png"
clone = os.environ.get("GH_CLONE", "/home/claude/tirumala-status-cards")
if not os.path.isdir(os.path.join(clone, ".git")):
    subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{repo}", clone], check=True)
git = lambda *a: subprocess.run(["git", "-C", clone, *a], check=True, capture_output=True, text=True).stdout.strip()
git("pull", "--ff-only", "-q")
os.makedirs(os.path.join(clone, "posts"), exist_ok=True)
with open(img, "rb") as src, open(os.path.join(clone, dest), "wb") as out:
    out.write(src.read())
git("add", dest)
git("-c", "user.name=tirumaladarshaninfo-lab",
    "-c", "user.email=tirumaladarshaninfo-lab@users.noreply.github.com",
    "commit", "-qm", f"Tirumala card {stamp}")
git("push", "-q", "origin", "HEAD")
branch = git("rev-parse", "--abbrev-ref", "HEAD")
image_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{dest}"
time.sleep(8)  # let GitHub's raw CDN see the new file

# 2. Create the media container
if mode == "story":
    c = call("POST", f"{ig_user}/media", image_url=image_url, media_type="STORIES")
else:
    c = call("POST", f"{ig_user}/media", image_url=image_url, caption=open(cap_file).read().strip())
cid = c["id"]

# 3. Wait until Instagram has processed it
for _ in range(20):
    s = call("GET", cid, fields="status_code").get("status_code")
    if s == "FINISHED":
        break
    if s in ("ERROR", "EXPIRED"):
        sys.exit(f"Container {cid} failed: {s}")
    time.sleep(3)

# 4. Publish and report the link
pid = call("POST", f"{ig_user}/media_publish", creation_id=cid)["id"]
link = call("GET", pid, fields="permalink").get("permalink", "")
print(json.dumps({"posted": mode, "media_id": pid, "permalink": link, "image_url": image_url}))
