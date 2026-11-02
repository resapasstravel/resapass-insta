"""Shared Resapass visual style (A Editorial, chosen by Olivier on 2 Nov 2026).
Serif titles (Fraunces, OFL) + Inter, cream inner slides, harmonised photo grade."""
import base64, io, pathlib
from PIL import Image, ImageEnhance
ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "tools" / "brand"
NAVY, DEEP, CREAM, SKY = "#29265C", "#19173D", "#F3EEE6", "#69B9E8"

def b64(p, mime): return f"data:{mime};base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()

FONTS = "".join(
    f"@font-face{{font-family:'Fraunces';src:url({b64(B/'fonts'/f'fraunces-latin-{w}-{s}.woff2', 'font/woff2')});font-weight:{w};font-style:{s}}}"
    for w in (300, 400, 500) for s in ("normal", "italic"))
LOGO = {k: b64(B / f"logo-{k}.png", "image/png") for k in ("white", "color")}
ICON = {k: b64(B / f"icon-{k}.png", "image/png") for k in ("white", "color")}

def grade_img(name):
    """Same soft, warm grade on every photo so the grid feels like one set."""
    im = Image.open(ROOT / "photos" / name).convert("RGB")
    im = ImageEnhance.Color(im).enhance(0.86)
    im = ImageEnhance.Contrast(im).enhance(0.94)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04 + 4)))
    g = g.point(lambda v: min(255, int(v + 2)))
    b = b.point(lambda v: min(255, int(v * 0.95 + 6)))
    return Image.merge("RGB", (r, g, b))

def grade_uri(name):
    buf = io.BytesIO(); grade_img(name).save(buf, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def split_title(t):
    """'Barcelona|where to stay, by vibe' -> ('Barcelona', 'where to stay, by vibe'): second part set in italic."""
    main, _, it = (t or "").partition("|")
    return main.strip(), it.strip()
