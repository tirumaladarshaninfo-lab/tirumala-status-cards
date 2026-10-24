"""Turn a 1080x1350 card into a 1080x1920 Reel with original devotional music.
Usage: python3 make_reel.py card.png out.mp4   (downloads a random track from the repo if music/ is missing)"""
import os, random, subprocess, sys, urllib.request
card, out = sys.argv[1], sys.argv[2]
tracks = ["track1_mohanam", "track2_hindolam", "track3_shankarabharanam", "track4_madhyamavati", "track5_mohanam", "track6_hindolam"]
name = random.choice(tracks) + ".m4a"
local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music", name)
if not os.path.exists(local):
    local = name
    urllib.request.urlretrieve(f"https://raw.githubusercontent.com/tirumaladarshaninfo-lab/tirumala-status-cards/main/music/{name}", local)
vf = ("[0:v]scale=1080:1350,pad=1080:1920:0:285:color=0x120d1c,"
      "zoompan=z='min(1+0.0005*on,1.06)':d=600:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,format=yuv420p[v]")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", card, "-i", local, "-filter_complex", vf,
                "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                "-c:a", "aac", "-b:a", "160k", "-t", "18", "-shortest", "-movflags", "+faststart", out], check=True)
print(out, name)
