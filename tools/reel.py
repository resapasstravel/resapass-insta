"""Render a Resapass reel (1080x1920 MP4, H.264 + silent AAC, 30 fps) from photos.

Post format in a week JSON:
  {"id": "w5-02", "date": "2026-11-03", "type": "reel",
   "scenes": [{"image": "p094.jpg", "kicker": "...", "title": "...", "body": "..."}, ...],   # 2 to 4 scenes
   "end": {"title": "...", "body": "..."},
   "caption": "..."}
Each photo scene lasts ~3.2 s with a slow pan + zoom and animated text; the end card is a brand slide.
Output: <id>.mp4 and <id>-cover.jpg (first scene, text visible) in the out dir.
"""
import base64, html, io, json, pathlib, subprocess, sys
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from style import FONTS, grade_img, split_title

W, H, FPS = 1080, 1920, 30
SCENE, END, FADE = 3.2, 2.6, 0.45
ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "tools" / "brand"
NAVY, DEEP, CREAM, SUN = "#29265C", "#19173D", "#F3EEE6", "#69B9E8"

def b64(p, mime="image/png"): return f"data:{mime};base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()
def esc(s): return html.escape(s or "")

BASE = f"""{FONTS}*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:transparent;font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased}}
.k{{font-weight:600;font-size:28px;letter-spacing:.28em;text-transform:uppercase;color:#fff;opacity:.92}}
.rule{{width:60px;height:2px;background:#fff;opacity:.6;margin:28px 0 32px}}
h1{{font-family:'Fraunces',serif;font-weight:400;font-size:118px;line-height:1.03;letter-spacing:-.015em;color:#fff}}
.it{{font-family:'Fraunces',serif;font-style:italic;font-weight:300;font-size:76px;line-height:1.12;color:#fff;margin-top:12px}}
p{{font-size:42px;line-height:1.38;color:#fff;opacity:.9}}
.btn{{display:inline-block;background:{CREAM};color:{NAVY};font-weight:600;font-size:36px;letter-spacing:.04em;padding:26px 48px;border-radius:999px}}"""

def text_html(sc):
    kick = f'<div class="k">{esc(sc.get("kicker"))}</div><div class="rule"></div>' if sc.get("kicker") else ""
    main, it = split_title(sc["title"])
    itl = f'<div class="it">{esc(it)}</div>' if it else ""
    body = f'<div style="height:30px"></div><p>{esc(sc.get("body"))}</p>' if sc.get("body") and not it else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE}</style></head><body>'
            f'<div style="position:absolute;left:88px;right:170px;bottom:430px">{kick}<h1>{esc(main)}</h1>{itl}{body}</div>'
            f'</body></html>')

def grad_html():
    logo = b64(B / "logo-white.png")
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE}</style></head><body>'
            f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(20,18,40,.32) 0%,rgba(20,18,40,0) 22%,rgba(20,18,40,0) 42%,rgba(20,18,40,.8) 82%,rgba(20,18,40,.88) 100%)"></div>'
            f'<img src="{logo}" style="position:absolute;top:150px;left:88px;height:54px"></body></html>')

def end_html(e):
    icon, logo = b64(B / "icon-white.png"), b64(B / "logo-white.png")
    main, it = split_title(e["title"])
    itl = f'<div class="it">{esc(it)}</div>' if it else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE}</style></head><body>'
            f'<div style="position:absolute;inset:0;background:radial-gradient(120% 80% at 85% 0%, #34397A 0%, {NAVY} 45%, {DEEP} 100%)"></div>'
            f'<div style="position:absolute;left:88px;right:120px;top:560px">'
            f'<img src="{icon}" style="height:96px;opacity:.9"><div style="height:70px"></div>'
            f'<h1>{esc(main)}</h1>{itl}<div class="rule"></div><p>{esc(e.get("body"))}</p>'
            f'<div style="height:60px"></div><div class="btn">resapass.co</div></div>'
            f'<img src="{logo}" style="position:absolute;bottom:200px;left:88px;height:52px;opacity:.92"></body></html>')

def shoot(pg, doc, transparent=True):
    pg.set_content(doc); pg.wait_for_timeout(80)
    return Image.open(io.BytesIO(pg.screenshot(type="png", omit_background=transparent))).convert("RGBA")

def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)

def photo_frame(img, t, dur, direction):
    """Slow pan across the spare width of a 4:5 photo plus a gentle zoom, with subpixel boxes (no jitter)."""
    iw, ih = img.size
    p = t / dur
    z = 1.0 + 0.07 * p
    bh = ih / z; bw = bh * W / H
    if bw > iw: bw = iw; bh = bw * H / W
    span = iw - bw
    fx = 0.15 + 0.7 * p if direction > 0 else 0.85 - 0.7 * p
    x0 = span * fx; y0 = (ih - bh) / 2
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh)).convert("RGBA")

def text_layer(txt, t, dur):
    a = min(ease((t - 0.3) / 0.6), ease((dur - FADE - t) / 0.35))
    if a <= 0: return None
    dy = int(round(60 * (1 - a)))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); layer.paste(txt, (0, dy))
    if a < 1:
        alpha = layer.getchannel("A").point(lambda v: int(v * a)); layer.putalpha(alpha)
    return layer

def render(post, out, pg):
    out = pathlib.Path(out)
    grad = shoot(pg, grad_html())
    scenes = []
    for k, sc in enumerate(post["scenes"]):
        img = grade_img(sc["image"])
        scenes.append(("photo", img, shoot(pg, text_html(sc)), 1 if k % 2 == 0 else -1, SCENE))
    endimg = shoot(pg, end_html(post["end"]), transparent=False)
    scenes.append(("end", endimg, None, 0, END))

    def frame(sc, t):
        kind, img, txt, d, dur = sc
        if kind == "end":
            z = 1.0 + 0.03 * t / dur; bw, bh = W / z, H / z
            return img.resize((W, H), Image.LANCZOS, box=((W - bw) / 2, (H - bh) / 2, (W + bw) / 2, (H + bh) / 2))
        f = photo_frame(img, t, dur, d); f.alpha_composite(grad)
        tl = text_layer(txt, t, dur)
        if tl is not None: f.alpha_composite(tl)
        return f

    # cover: first scene, text fully in
    cov = frame(scenes[0], 1.2).convert("RGB")
    cov.save(out / f'{post["id"]}-cover.jpg', "JPEG", quality=92)

    mp4 = out / f'{post["id"]}.mp4'
    total = sum(s[4] for s in scenes) - FADE * (len(scenes) - 1)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-shortest", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
        "-r", str(FPS), "-g", str(FPS * 2), "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(mp4)],
        stdin=subprocess.PIPE)
    starts, s = [], 0.0
    for sc in scenes: starts.append(s); s += sc[4] - FADE
    for n in range(int(round(total * FPS))):
        t = n / FPS
        idx = [i for i, st in enumerate(starts) if st <= t < st + scenes[i][4]]
        if len(idx) == 1:
            i = idx[0]; img = frame(scenes[i], t - starts[i])
        else:
            a, b = idx[0], idx[-1]
            fa, fb = frame(scenes[a], t - starts[a]), frame(scenes[b], t - starts[b])
            img = Image.blend(fa.convert("RGB"), fb.convert("RGB"), ease((t - starts[b]) / FADE))
        ff.stdin.write(img.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    if ff.returncode: raise RuntimeError("ffmpeg failed")
    return [mp4.name, f'{post["id"]}-cover.jpg']

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    posts = [p for p in json.load(open(sys.argv[1])) if p.get("type") == "reel"]
    pathlib.Path(sys.argv[2]).mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        for post in posts: print(render(post, sys.argv[2], pg))
        b.close()
