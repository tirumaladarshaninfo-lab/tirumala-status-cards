"""Tirumala Darshan Info – Live Status card on the user's own template.
Usage: python3 tdi_live.py data.json out.png [background.png]"""
import json, sys, html, base64, os
from playwright.sync_api import sync_playwright
d = json.load(open(sys.argv[1])); out = sys.argv[2]
bg = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "tdi_live_bg.png")
B64 = base64.b64encode(open(bg, "rb").read()).decode()
E = lambda k, dv="Not available": html.escape(str(d.get(k) or dv))
FONT = "/usr/share/fonts/truetype/google-fonts/"
def ff(w, f):
    p = FONT + f
    if not os.path.exists(p): return ""
    return "@font-face{font-family:P;src:url(data:font/ttf;base64," + base64.b64encode(open(p,"rb").read()).decode() + ") format('truetype');font-weight:" + str(w) + "}"
fonts = ff(400,"Poppins-Regular.ttf") + ff(500,"Poppins-Medium.ttf") + ff(700,"Poppins-Bold.ttf")
def fit(k, base, maxlen):
    v = str(d.get(k) or "")
    return base if len(v) <= maxlen else max(15, int(base * maxlen / len(v)))
lvl = str(d.get("crowd", "")).lower()
crowd_col = "#e0262b" if ("high" in lvl or "extreme" in lvl) else ("#e3a10b" if "moderate" in lvl else ("#2a9d4b" if "low" in lvl else "#777"))
tr = str(d.get("trend", "")).lower()
arrow = ('<span style="color:#e0262b">↗</span>' if "incr" in tr else '<span style="color:#3fbf63">↘</span>' if "decr" in tr else '<span style="color:#f3c75a">→</span>')
sv = str(d.get("srivani_status", "")).lower()
sv_col = "#e0262b" if ("sold" in sv or "suspend" in sv) else ("#2a9d4b" if "avail" in sv else "#777")
avail = str(d.get("srivani_available", ""))
avail_col = "#ff3b3b" if avail.strip() in ("0", "") else "#5fe08a"
ssd_done = bool(d.get("ssd_completed"))
status_icon = ('<div class="ico red">–</div>' if ssd_done else '<div class="ico green">✓</div>')
def lines(k, dv=""):
    return "<br>".join(html.escape(x) for x in str(d.get(k) or dv).split("\n"))
best = lines("best_time", "Not available")
page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1122px;height:1402px;position:relative;font-family:P,sans-serif;background:url(data:image/png;base64,{B64}) 0 0/1122px 1402px no-repeat;overflow:hidden}}
.a{{position:absolute;white-space:nowrap}}
.pill{{position:absolute;display:flex;align-items:center;justify-content:center;border-radius:10px;font-weight:500;text-align:center;line-height:1.1;box-shadow:inset 0 2px 0 rgba(255,255,255,.25),0 2px 6px rgba(0,0,0,.4)}}
.gold{{color:#f6c453;font-weight:500}} .wh{{color:#fff}}
.val{{position:absolute;left:476px;color:#f6c453;font-weight:500;font-size:24px;white-space:nowrap;text-shadow:0 1px 2px #000}}
.r{{position:absolute;color:#f6c453;font-weight:500;font-size:24px;text-align:right;white-space:nowrap;text-shadow:0 1px 2px #000}}
.lab{{position:absolute;color:#fff;font-size:19.5px;line-height:1.3;text-shadow:0 1px 2px #000}}
.ico{{position:absolute;left:62px;top:1136px;width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:30px;color:#fff}}
.ico.red{{background:#e0262b}} .ico.green{{background:#2a9d4b;font-size:24px}}
</style></head><body>
<div class="a wh" style="left:264px;top:318px;font-size:25px;font-weight:500;text-shadow:0 1px 3px #000">{E('updated_date')} <span class="gold" style="color:#f6c453">{E('updated_time')}</span> {E('updated_ampm','IST')}</div>
<div class="pill" style="left:116px;top:404px;width:148px;height:43px;background:{crowd_col};color:#fff;font-size:{22 if len(str(d.get('crowd','')))<10 else 17}px;text-transform:uppercase">{E('crowd')}</div>
<div class="a wh" style="left:368px;top:407px;font-size:20px;text-shadow:0 1px 2px #000">{E('trend_word')} <span style="font-size:30px;font-weight:700;vertical-align:-3px">{arrow}</span></div>
<div class="pill" style="left:612px;top:404px;width:180px;height:54px;background:linear-gradient(#f9df8a,#f2c24f);color:#1d1406;font-size:{19 if len(str(d.get('best_time','')))<26 else 15}px">{best}</div>
<div class="val" style="top:{480 if len(str(d.get('location','')))<=12 else 476}px;font-size:{24 if len(str(d.get('location','')))<=12 else 19}px;white-space:normal;width:175px;line-height:1.1">{E('location')}</div>
<div class="val" style="top:523px">{E('waiting')}</div>
<div class="val" style="top:566px">{E('completed')}</div>
<div class="lab" style="left:116px;top:610px">{lines('capacity_label','Balance capacity\nfor the day')}</div>
<div class="val" style="top:627px">{E('capacity_value')}</div>
<div class="val" style="top:675px">{E('compartments')}</div>
<div class="lab" style="left:116px;top:722px">{lines('queue_note','')}</div>
<div class="pill" style="left:207px;top:938px;width:155px;height:40px;background:linear-gradient(#ff3b3b,#d71920);color:#fff;font-size:23px">{E('free_time')}</div>
<div class="pill" style="left:553px;top:945px;width:173px;height:40px;background:linear-gradient(#ffe48a,#f4c34e);color:#1d1406;font-size:23px">{E('ssd_time')}</div>
<div class="pill" style="left:913px;top:941px;width:155px;height:40px;background:linear-gradient(#7be36d,#3fb43a);color:#0f2a0c;font-size:23px">{E('sed_time')}</div>
<div class="a gold" style="left:130px;top:1094px;font-size:{fit('ssd_released',23,15)}px">{E('ssd_released')}</div>
{status_icon}
<div class="a wh" style="left:130px;top:1140px;font-size:{fit('ssd_status',20,21)}px;text-shadow:0 1px 2px #000">{E('ssd_status','Status not available')}</div>
<div class="a gold" style="left:209px;top:1180px;font-size:{fit('ssd_value',24,10)}px">{E('ssd_value')}</div>
<div class="a gold" style="left:209px;top:1222px;font-size:{fit('dd_value',24,10)}px">{E('dd_value')}</div>
<div class="r" style="right:{1122-738}px;top:1069px">{E('quota')}</div>
<div class="r" style="right:{1122-738}px;top:1110px">{E('registered')}</div>
<div class="r" style="right:{1122-738}px;top:1160px">{E('awaiting_keys')}</div>
<div class="r" style="right:{1122-738}px;top:1221px">{E('rooms_left')}</div>
<div class="pill" style="left:840px;top:1070px;width:210px;height:42px;background:linear-gradient({sv_col},{sv_col});color:#fff;font-size:{26 if len(str(d.get('srivani_status','')))<10 else 20}px;font-weight:700;border-radius:8px">{E('srivani_status')}</div>
<div class="r" style="right:{1122-1050}px;top:1131px">{E('srivani_quota')}</div>
<div class="r" style="right:{1122-1050}px;top:1175px">{E('srivani_issued')}</div>
<div class="r" style="right:{1122-1050}px;top:1220px;color:{avail_col}">{E('srivani_available')}</div>
<div class="a" style="left:0;right:0;top:1384px;text-align:center;font-size:12px;color:rgba(255,240,210,.85)">{E('source','')}</div>
</body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1122, "height": 1402})
    pg.set_content(page); pg.wait_for_timeout(400); pg.screenshot(path=out); b.close()
print(out)
