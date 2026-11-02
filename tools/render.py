"""Render Resapass Instagram posts (1080x1350 JPG) from a week JSON file. Style: A Editorial (see style.py).

Usage: python3 render.py week.json out/
Titles may contain "|": the part after it is set on its own line in italic ("Barcelona|where to stay, by vibe").
"""
import json, sys, html, pathlib, io
from playwright.sync_api import sync_playwright
from PIL import Image
from style import FONTS, LOGO, ICON, NAVY, DEEP, CREAM, SKY, grade_uri, split_title

W, H = 1080, 1350
DISCLAIMER = "Average across our price checks vs major booking sites. Not guaranteed on every hotel or date."

CSS = f"""{FONTS}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased}}
.s{{width:{W}px;height:{H}px;position:relative;overflow:hidden}}
.dark{{background:radial-gradient(120% 90% at 85% 0%, #34397A 0%, {NAVY} 45%, {DEEP} 100%);color:#fff}}
.light{{background:{CREAM};color:{NAVY}}}
.k{{font-weight:600;font-size:24px;letter-spacing:.28em;text-transform:uppercase}}
.light .k{{color:{SKY}}}
.rule{{width:56px;height:2px;background:currentColor;opacity:.55}}
.serif{{font-family:'Fraunces',serif;font-weight:400;letter-spacing:-.015em}}
.it{{font-family:'Fraunces',serif;font-style:italic;font-weight:300}}
p{{font-size:38px;line-height:1.45;opacity:.82}}
.num{{font-family:'Fraunces',serif;font-style:italic;font-weight:300;font-size:150px;line-height:1;color:{SKY}}}
.btn{{display:inline-block;background:{CREAM};color:{NAVY};font-weight:600;font-size:32px;letter-spacing:.04em;padding:24px 44px;border-radius:999px}}
.foot{{position:absolute;left:92px;right:92px;bottom:66px;display:flex;justify-content:space-between;align-items:center;font-weight:600;font-size:24px;letter-spacing:.08em}}
.light .foot{{opacity:.5}}
.box{{position:absolute;left:92px;right:92px}}
"""

def esc(s): return html.escape(s or "")

def foot(i, n, light=False, logo=True):
    ctr = f"{i+1} / {n}" if n > 1 else ""
    left = f'<img src="{LOGO["white"]}" style="height:34px;opacity:.92">' if logo and not light else "<span>RESAPASS</span>"
    right = ctr if i < n - 1 or n == 1 else "resapass.co"
    if n == 1: right = "resapass.co"
    return f'<div class="foot">{left}<span>{esc(right)}</span></div>'

def title_html(t, size, it_size=None, color=""):
    main, it = split_title(t)
    it_size = it_size or int(size * 0.66)
    out = f'<div class="serif" style="font-size:{size}px;line-height:1.03;{color}">{esc(main)}</div>'
    if it: out += f'<div class="it" style="font-size:{it_size}px;line-height:1.12;margin-top:12px;{color}">{esc(it)}</div>'
    return out

def tsize(t, big, mid, small):
    main, _ = split_title(t); n = len(main)
    return big if n <= 18 else mid if n <= 30 else small

def slide(sl, i, n):
    t = sl["tpl"]; light = False
    if t == "photo":
        img = grade_uri(sl["image"])
        kick = f'<div class="k" style="opacity:.92">{esc(sl.get("kicker"))}</div><div class="rule" style="margin:26px 0 30px;background:#fff"></div>' if sl.get("kicker") else ""
        _, it = split_title(sl.get("title"))
        body = "" if it or not sl.get("body") else f'<div style="height:26px"></div><p style="font-size:34px;color:#fff;opacity:.88">{esc(sl["body"])}</p>'
        inner = (f'<div style="position:absolute;inset:0;background:url({img}) center/cover"></div>'
                 f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(20,18,40,.28) 0%,rgba(20,18,40,0) 24%,rgba(20,18,40,0) 48%,rgba(20,18,40,.78) 100%)"></div>'
                 f'<div class="box" style="bottom:150px;color:#fff">{kick}{title_html(sl.get("title"), tsize(sl.get("title"), 104, 88, 74))}{body}</div>')
        cls = "dark"
    elif t in ("point", "place"):
        cls = "light"; light = True
        tag = f'<div class="k">{esc(sl["tag"])}</div><div style="height:22px"></div>' if t == "place" else ""
        size = 96 if t == "place" else tsize(sl["title"], 92, 82, 70)
        inner = (f'<div class="box num" style="top:110px">{esc(sl["n"])}</div>'
                 f'<div class="box" style="bottom:200px">{tag}{title_html(sl["title"], size)}'
                 f'<div class="rule" style="margin:40px 0"></div><p>{esc(sl["body"])}</p></div>')
    elif t == "cover":
        cls = "dark"
        inner = (f'<img src="{ICON["white"]}" style="position:absolute;top:96px;right:92px;height:70px;opacity:.9">'
                 f'<div class="box k" style="top:110px;color:{SKY}">{esc(sl["kicker"])}</div>'
                 f'<div class="box" style="bottom:190px">{title_html(sl["title"], tsize(sl["title"], 112, 96, 80))}'
                 f'<div class="rule" style="margin:40px 0;background:#fff"></div><p>{esc(sl.get("sub"))}</p></div>')
    elif t in ("stat", "bigstat"):
        cls = "dark"
        kick = f'<div class="box k" style="top:110px;color:{SKY}">{esc(sl.get("kicker"))}</div>' if sl.get("kicker") else ""
        inner = (f'{kick}<div class="box" style="top:300px"><div class="it" style="font-size:300px;line-height:.9;color:{SKY}">{esc(sl["big"])}</div>'
                 f'<div style="height:30px"></div>{title_html(sl["title"], 72)}<div style="height:30px"></div><p>{esc(sl["body"])}</p></div>'
                 f'<p class="box" style="bottom:140px;font-size:22px;opacity:.55">{DISCLAIMER}</p>')
    elif t == "manifesto":
        cls = "dark"
        lines = "".join(f'<div class="serif" style="font-size:80px;line-height:1.1;opacity:.45">{esc(l)}</div>' for l in sl["lines"])
        inner = (f'<div class="box" style="bottom:200px">{lines}<div style="height:36px"></div>'
                 f'<div class="it" style="font-size:92px;line-height:1.05;color:{SKY}">{esc(sl["title"])}</div>'
                 f'<div class="rule" style="margin:40px 0;background:#fff"></div><p>{esc(sl["body"])}</p></div>')
    elif t == "question":
        cls = "dark"
        inner = (f'<div class="box k" style="top:110px;color:{SKY}">{esc(sl["kicker"])}</div>'
                 f'<div class="box" style="bottom:190px">{title_html(sl["title"], 120)}<div style="height:40px"></div>'
                 f'<p>{esc(sl["body"])}</p><div style="height:50px"></div><div class="btn">Tell us below</div></div>')
    elif t == "cta":
        cls = "dark"
        inner = (f'<img src="{ICON["white"]}" style="position:absolute;top:96px;left:92px;height:70px;opacity:.9">'
                 f'<div class="box" style="top:480px">{title_html(sl["title"], 100)}<div class="rule" style="margin:40px 0;background:#fff"></div>'
                 f'<p>{esc(sl["body"])}</p><div style="height:56px"></div><div class="btn">resapass.co</div></div>')
    else:
        raise ValueError(t)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="s {cls}">{inner}{foot(i, n, light, logo=(t != "cta"))}</div></body></html>'

def main(src, out):
    posts = json.load(open(src))
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        rpg = None
        for post in posts:
            if post.get("type") == "reel":
                import reel
                rpg = rpg or b.new_page(viewport={"width": reel.W, "height": reel.H})
                post["images"] = reel.render(post, out, rpg)
                continue
            n = len(post["slides"]); files = []
            for i, sl in enumerate(post["slides"]):
                pg.set_content(slide(sl, i, n)); pg.wait_for_timeout(120)
                png = pg.screenshot(type="png")
                name = f'{post["id"]}-{i+1}.jpg'
                Image.open(io.BytesIO(png)).convert("RGB").save(out / name, "JPEG", quality=92)
                files.append(name)
            post["images"] = files
        b.close()
    json.dump(posts, open(out / "queue.json", "w"), indent=2, ensure_ascii=False)
    print("rendered", sum(len(p["images"]) for p in posts), "files")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
