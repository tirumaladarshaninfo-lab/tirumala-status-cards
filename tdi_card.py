"""Tirumala Darshan Info card template. Usage: python3 tdi_card.py data.json out.png
data.json: {title, date_label, updated, left:{name,sub,rows:[[a,b],...],total:[label,value], head:[c1,c2]}, right:{...same}, info:[4 strings], official:bool, source}"""
import json, sys, html
from playwright.sync_api import sync_playwright
d = json.load(open(sys.argv[1])); out = sys.argv[2]
E = lambda s: html.escape(str(s))
def panel(p, cls):
    rows = "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in p["rows"])
    tot = p.get("total")
    tot = f'<tr class="tot"><td>{E(tot[0])}</td><td class="big">{E(tot[1])}</td></tr>' if tot else ""
    note = f'<div class="pnote">{E(p["note"])}</div>' if p.get("note") else ""
    return f'''<div class="panel {cls}"><div class="ptop"><div class="dome">🛕</div></div>
<div class="pname"><div class="n">{E(p["name"])}</div><div class="s">{E(p["sub"])}</div></div>
<table><tr class="h"><th>{E(p["head"][0])}</th><th>{E(p["head"][1])}</th></tr>{rows}{tot}</table>{note}</div>'''
icons = ["👥", "🪪", "🙏", "🚫"]
info = "".join(f'<div class="ii"><div class="ic">{icons[i%4]}</div><div>{E(t)}</div></div>' for i, t in enumerate(d["info"]))
strip = ("<div class=\"strip\">" + "".join(f"<div><b>{E(k)}:</b> {E(v)}</div>" for k, v in d.get("strip", [])) + "</div>") if d.get("strip") else ""
badge = ('<div class="off ok">✔ TTD OFFICIAL FIGURES</div>' if d.get("official")
         else '<div class="off">UNOFFICIAL UPDATE · NOT FROM TTD</div>')
page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:'DejaVu Sans',Inter,sans-serif;position:relative;overflow:hidden;
background:radial-gradient(ellipse at 50% 18%,#3a5a7a 0%,#1d2f4a 30%,#120d1c 60%),#120d1c}}
.frame{{position:absolute;inset:0;border:16px solid transparent;border-image:linear-gradient(180deg,#f7d77a,#b8862b,#f7d77a,#8a5a14) 1}}
.pillar{{position:absolute;top:0;bottom:120px;width:44px;background:repeating-linear-gradient(180deg,#c99a3c 0 18px,#f5d27a 18px 26px,#8a5a14 26px 30px);opacity:.95}}
.pillar.l{{left:16px}} .pillar.r{{right:16px}}
.lamp{{position:absolute;bottom:126px;font-size:34px}} .lamp.l{{left:22px}} .lamp.r{{right:22px}}
.wrap{{position:absolute;left:76px;right:76px;top:34px;bottom:0;display:flex;flex-direction:column;align-items:center}}
.brand{{font-family:'DejaVu Serif',Georgia,serif;font-size:58px;font-weight:700;color:#f5c94c;white-space:nowrap;
text-shadow:0 3px 0 #7a4b0e,0 0 18px rgba(245,201,76,.45);letter-spacing:1px}}
.tags{{color:#f3e2b5;font-size:15px;letter-spacing:2px;margin-top:2px}}
.ttl{{margin-top:18px;width:100%;background:linear-gradient(180deg,#9b1b1b,#5e0b0e);border:4px solid #e6b54a;border-radius:60px;
padding:12px 10px 18px;text-align:center;box-shadow:0 6px 0 #3d0608}}
.ttl h1{{font-family:'DejaVu Serif',Georgia,serif;font-size:46px;white-space:nowrap;color:#fff3cf;letter-spacing:2px}}
.date{{margin-top:-14px;background:linear-gradient(180deg,#1f3a73,#0e1e46);color:#fff;border:3px solid #e6b54a;border-radius:30px;
padding:6px 30px;font-size:26px;font-weight:700;z-index:2}}
.upd{{margin-top:6px;color:#f3e2b5;font-size:19px}}
.off{{margin-top:6px;font-size:16px;font-weight:700;letter-spacing:1px;color:#f5c94c;border:2px solid #f5c94c;border-radius:20px;padding:4px 16px}}
.off.ok{{color:#9be7b5;border-color:#3fae6a}}
.panels{{display:flex;gap:22px;width:100%;margin-top:16px}}
.panel{{flex:1;background:#fff8e6;border:5px solid #e6b54a;border-radius:18px;overflow:hidden;box-shadow:0 0 0 3px #7a4b0e}}
.ptop{{height:96px;background:linear-gradient(180deg,#7fb0e0,#e9d29a);display:flex;align-items:center;justify-content:center}}
.dome{{font-size:60px}}
.pname{{text-align:center;padding:10px 6px 8px;color:#fff}}
.green .pname{{background:linear-gradient(180deg,#1f6a3a,#0f4424)}} .red .pname{{background:linear-gradient(180deg,#a3171c,#6a0b10)}}
.pname .n{{font-size:38px;font-weight:800;letter-spacing:1px}} .pname .s{{font-size:19px;font-weight:700;color:#f5d77a}}
table{{width:100%;border-collapse:collapse;font-size:25px;color:#2a1608}}
th{{font-size:20px;color:#fff;padding:10px 4px}} .green th{{background:#14502b}} .red th{{background:#7d0f14}}
td{{text-align:center;padding:12px 4px;border-bottom:1px solid #e3cfa0}}
td+td,th+th{{border-left:1px solid #e3cfa0}}
.tot td{{background:#f5d77a;font-weight:800;font-size:25px}} .tot .big{{font-size:44px;color:#8a0f14}}
.pnote{{font-size:19px;color:#5a3a10;text-align:center;padding:8px 10px;background:#fbefcc}}
.ib{{margin-top:30px;width:100%;background:#fff8e6;border:4px solid #e6b54a;border-radius:18px;padding:28px 20px 14px;position:relative}}
.ib .hd{{font-size:22px !important;position:absolute;top:-22px;left:50%;transform:translateX(-50%);background:linear-gradient(180deg,#9b1b1b,#5e0b0e);color:#fff3cf;
border:3px solid #e6b54a;border-radius:30px;padding:6px 30px;font-family:'DejaVu Serif',serif;font-size:26px;font-weight:700;white-space:nowrap}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px 24px}}
.strip{{margin-top:18px;width:100%;background:linear-gradient(180deg,#1f3a73,#0e1e46);border:3px solid #e6b54a;border-radius:16px;padding:12px 22px;color:#fff3cf}}
.strip div{{font-size:20px;padding:5px 0;border-bottom:1px solid rgba(230,181,74,.35)}} .strip div:last-child{{border:none}} .strip b{{color:#f5c94c}}
.ii{{display:flex;gap:12px;align-items:center;font-size:18px;color:#3a2410;line-height:1.3}}
.ic{{flex:0 0 50px;height:50px;border-radius:50%;background:#7d0f14;display:flex;align-items:center;justify-content:center;font-size:22px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:112px;background:linear-gradient(180deg,#6a0b10,#3d0608);border-top:4px solid #e6b54a;
display:flex;align-items:center;justify-content:space-around;color:#f3e2b5;font-size:14px;padding:0 30px;gap:18px;text-align:center}}
.foot b{{display:block;font-size:34px;color:#f5c94c}} .foot .c b{{font-size:18px;color:#fff;margin-top:2px}}
.src{{margin-top:auto;margin-bottom:124px;font-size:14px;color:#d9c79d;text-align:center}}
</style></head><body>
<div class="pillar l"></div><div class="pillar r"></div><div class="lamp l">🪔</div><div class="lamp r">🪔</div>
<div class="wrap">
<div class="brand">Tirumala Darshan Info</div>
<div class="tags">OFFICIAL UPDATES &nbsp;|&nbsp; DARSHAN INFO &nbsp;|&nbsp; TTD SERVICES &nbsp;|&nbsp; PILGRIM GUIDE</div>
<div class="ttl"><h1>{E(d['title'])}</h1></div>
<div class="date">{E(d['date_label'])}</div>
<div class="upd">({E(d['updated'])})</div>
{badge}
<div class="panels">{panel(d['left'],'green')}{panel(d['right'],'red')}</div>
{strip}<div class="ib"><div class="hd">IMPORTANT INFORMATION</div><div class="grid">{info}</div></div>
<div class="src">{E(d['source'])}</div>
</div>
<div class="foot"><div>TTD Call Center (24x7)<b>155257</b></div>
<div class="c">Official Website<b>ttdevasthanams.ap.gov.in</b></div>
<div class="c">TTD Mobile App<b>TTDevasthanams</b></div>
<div class="c">Follow for Daily Updates<b>@tirumaladarshaninfo</b></div></div>
<div class="frame"></div>
</body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width":1080,"height":1350})
    pg.set_content(page); pg.wait_for_timeout(300)
    z = 1.0
    while z > 0.62:
        fits = pg.evaluate("() => document.querySelector('.src').getBoundingClientRect().bottom <= document.querySelector('.foot').getBoundingClientRect().top - 8 && document.querySelector('.ib').getBoundingClientRect().bottom <= document.querySelector('.src').getBoundingClientRect().top")
        if fits: break
        z -= 0.03
        pg.evaluate(f"() => document.querySelectorAll('.panels,.strip,.ib').forEach(e => e.style.zoom = {z})")
        pg.wait_for_timeout(50)
    pg.screenshot(path=out); b.close()
print(out)
