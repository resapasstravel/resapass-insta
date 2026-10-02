"""Render Resapass Instagram posts (1080x1350 JPG) from a week JSON file.

Usage: python3 render.py week.json out/
"""
import json, sys, html, pathlib, io, base64
B=pathlib.Path(__file__).parent/"brand"
def b64(n): return "data:image/png;base64,"+base64.b64encode((B/n).read_bytes()).decode()
LOGO={k:b64(f"logo-{k}.png") for k in ("white","color")}
ICON={k:b64(f"icon-{k}.png") for k in ("white","color")}
from playwright.sync_api import sync_playwright
from PIL import Image

W, H = 1080, 1350
NAVY, DEEP, CREAM, SUN, INK = "#29265C", "#19173D", "#F3F7FB", "#69B9E8", "#29265C"

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased}}
.s{{width:{W}px;height:{H}px;position:relative;padding:96px 88px;display:flex;flex-direction:column}}
.dark{{background:{NAVY};color:{CREAM}}}
.deep{{background:radial-gradient(120% 90% at 85% 0%, #3A3F86 0%, {NAVY} 45%, {DEEP} 100%);color:{CREAM}}}
.light{{background:{CREAM};color:{INK}}}
.sun{{background:{SUN};color:{DEEP}}}
.kicker{{font-weight:600;font-size:30px;letter-spacing:.14em;text-transform:uppercase;color:{SUN}}}
.light .kicker,.sun .kicker{{color:{NAVY}}}
h1{{font-family:'Inter Display';font-weight:800;font-size:104px;line-height:1.0;letter-spacing:-.035em}}
h2{{font-family:'Inter Display';font-weight:750;font-size:74px;line-height:1.05;letter-spacing:-.03em}}
p{{font-size:38px;line-height:1.4;font-weight:400;opacity:.86}}
.n{{font-family:'Inter Display';font-weight:800;font-size:200px;line-height:.8;letter-spacing:-.05em;color:{SUN}}}
.light .n{{color:{NAVY};opacity:.14}}
.big{{font-family:'Inter Display';font-weight:900;font-size:340px;line-height:.85;letter-spacing:-.06em;color:{SUN}}}
.sun .big{{color:{DEEP}}}
.tag{{display:inline-block;align-self:flex-start;background:{NAVY};color:{CREAM};font-weight:600;font-size:28px;letter-spacing:.06em;text-transform:uppercase;padding:14px 24px;border-radius:999px}}
.foot{{position:absolute;left:88px;right:88px;bottom:72px;display:flex;justify-content:space-between;align-items:center;font-size:28px;font-weight:600}}
.mark{{font-family:'Inter Display';font-weight:800;font-size:40px;letter-spacing:-.03em}}
.mark i{{font-style:normal;color:{SUN}}}
.light .mark i{{color:{NAVY};opacity:.5}}
.sun .mark i{{color:{CREAM}}}
.sun p{{opacity:.9}}
.ctr{{opacity:.6}}
.btn{{display:inline-block;align-self:flex-start;background:{SUN};color:{DEEP};font-weight:700;font-size:36px;padding:26px 44px;border-radius:999px}}
.rule{{width:120px;height:8px;background:{SUN};border-radius:4px}}
.light .rule{{background:{NAVY}}}
.line{{font-family:'Inter Display';font-weight:750;font-size:84px;line-height:1.08;letter-spacing:-.03em;opacity:.45}}
.grow{{flex:1}}
"""

def esc(s): return html.escape(s or "")

def foot(i, n, cls):
    arrow = "Swipe →" if n > 1 and i < n - 1 else ("resapass.co" if n == 1 or i == n - 1 else "")
    ctr = f"{i+1}/{n}" if n > 1 else ""
    logo = LOGO["color"] if cls == "light" else LOGO["white"]
    return f'<div class="foot"><img src="{logo}" style="height:46px"><div class="ctr">{ctr}</div><div>{esc(arrow)}</div></div>'

def slide(sl, i, n):
    t = sl["tpl"]
    if t == "cover":
        cls = "deep"
        body = f'<img src="{ICON["white"]}" style="position:absolute;top:84px;right:88px;height:84px"><div class="kicker">{esc(sl["kicker"])}</div><div class="grow"></div><h1>{esc(sl["title"])}</h1><div style="height:40px"></div><p>{esc(sl.get("sub"))}</p><div style="height:150px"></div>'
    elif t == "point":
        cls = "light"
        body = f'<div class="n">{esc(sl["n"])}</div><div class="grow"></div><h2>{esc(sl["title"])}</h2><div style="height:44px"></div><div class="rule"></div><div style="height:44px"></div><p>{esc(sl["body"])}</p><div style="height:150px"></div>'
    elif t == "place":
        cls = "light"
        body = f'<div class="n">{esc(sl["n"])}</div><div class="grow"></div><div class="tag">{esc(sl["tag"])}</div><div style="height:36px"></div><h1>{esc(sl["title"])}</h1><div style="height:40px"></div><p>{esc(sl["body"])}</p><div style="height:150px"></div>'
    elif t == "stat":
        cls = "dark"
        body = f'<div class="grow"></div><div class="big">{esc(sl["big"])}</div><div style="height:30px"></div><h2>{esc(sl["title"])}</h2><div style="height:30px"></div><p>{esc(sl["body"])}</p><div class="grow"></div><p style="font-size:24px;opacity:.55">Average across our price checks vs major booking sites. Not guaranteed on every hotel or date.</p><div style="height:110px"></div>'
    elif t == "bigstat":
        cls = "sun"
        body = f'<div class="kicker">{esc(sl["kicker"])}</div><div class="grow"></div><div class="big">{esc(sl["big"])}</div><div style="height:30px"></div><h2>{esc(sl["title"])}</h2><div style="height:30px"></div><p>{esc(sl["body"])}</p><div class="grow"></div><p style="font-size:24px;opacity:.65">Average across our price checks vs major booking sites. Not guaranteed on every hotel or date.</p><div style="height:110px"></div>'
    elif t == "manifesto":
        cls = "deep"
        lines = "".join(f'<div class="line">{esc(l)}</div>' for l in sl["lines"])
        body = f'<div class="grow"></div>{lines}<div style="height:40px"></div><h1 style="color:{SUN}">{esc(sl["title"])}</h1><div style="height:36px"></div><p>{esc(sl["body"])}</p><div class="grow"></div><div style="height:110px"></div>'
    elif t == "question":
        cls = "deep"
        body = f'<div class="kicker">{esc(sl["kicker"])}</div><div class="grow"></div><h1 style="font-size:132px">{esc(sl["title"])}</h1><div style="height:48px"></div><p>{esc(sl["body"])}</p><div style="height:60px"></div><div class="btn">Comment below ↓</div><div style="height:150px"></div>'
    elif t == "photo":
        img = pathlib.Path(__file__).resolve().parent.parent / "photos" / sl["image"]
        data = "data:image/jpeg;base64," + base64.b64encode(img.read_bytes()).decode()
        cls = "dark"
        kick = f'<div class="kicker" style="color:#fff">{esc(sl.get("kicker"))}</div>' if sl.get("kicker") else ""
        body = (f'<div style="position:absolute;inset:0;background:url({data}) center/cover"></div>'
                f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(25,23,61,.35) 0%,rgba(25,23,61,0) 30%,rgba(25,23,61,0) 50%,rgba(25,23,61,.85) 100%)"></div>'
                f'<div style="position:relative;display:flex;flex-direction:column;height:100%">{kick}<div class="grow"></div>'
                f'<h1 style="color:#fff">{esc(sl.get("title"))}</h1><div style="height:28px"></div><p style="color:#fff">{esc(sl.get("body"))}</p><div style="height:120px"></div></div>')
    elif t == "cta":
        cls = "dark"
        body = f'<div class="grow"></div><h1>{esc(sl["title"])}</h1><div style="height:44px"></div><p>{esc(sl["body"])}</p><div style="height:60px"></div><div class="btn">resapass.co</div><div class="grow"></div><div style="height:110px"></div>'
    else:
        raise ValueError(t)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="s {cls}">{body}{foot(i, n, cls)}</div></body></html>'

def main(src, out):
    posts = json.load(open(src))
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for post in posts:
            n = len(post["slides"]); files = []
            for i, sl in enumerate(post["slides"]):
                pg.set_content(slide(sl, i, n)); pg.wait_for_timeout(50)
                png = pg.screenshot(type="png")
                name = f'{post["id"]}-{i+1}.jpg'
                Image.open(io.BytesIO(png)).convert("RGB").save(out / name, "JPEG", quality=92)
                files.append(name)
            post["images"] = files
        b.close()
    json.dump(posts, open(out / "queue.json", "w"), indent=2, ensure_ascii=False)
    print("rendered", sum(len(p["images"]) for p in posts), "images")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
